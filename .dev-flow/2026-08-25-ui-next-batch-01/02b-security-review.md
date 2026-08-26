# 02b — Security review · `2026-08-25-ui-next-batch-01` · PDR gate

> Lens: `security-reviewer`. Reviews `PDR-design-proposal.md` §D2/§D3 against `01-requirements.md`
> HLR-N01/HLR-N02 and the code on disk. **No code was changed. Nothing under `prototypes/` was
> read or touched.** Artifact language English.

---

## 0 · Verdict

**`approved with conditions`** — 2 blockers, 6 majors, 6 minors. Every condition in §5 is
individually dischargeable and is written as requirement text ready to paste into
`01-requirements.md`.

The design is *directionally* right on both crossings: it isolates the OS-handler launch behind one
module, it picks a scheme allowlist rather than a denylist, and it names `Text.assemble` as the
render construction. It fails on two specifics, both of which I executed rather than argued:

1. **`kind == "file"` has no confinement.** The PDR signature drops the `workspace` parameter that
   `docs/ARCHITECTURE.md:147` already specifies, which structurally deletes the "path confinement
   under the workspace root" control that `docs/ARCHITECTURE.md:36` and risk `A-4`
   (`docs/ARCHITECTURE.md:287`) both mandate. Probe: `..`-traversal, `calc.exe` and `powershell.exe`
   all reached the launcher.
2. **Control-character injection is uncovered.** C-17 is scoped to Rich *markup*. Markup is handled
   correctly by the prescribed construction. Raw ANSI/OSC escapes are handled **nowhere** — proven
   to survive into the compositor segment stream from `Static`, from `Text.assemble`, and from the
   `Input` widget that LLR-N01.5 mandates. The batch's own hostile fixture (PDR §2) includes "an
   attachment caption containing an ANSI escape", so `AT-N01e` as scoped would test a control that
   does not exist.

### Threat model, stated plainly

This is a single-operator local TUI. `open_attachment` opening a local file is **not** remote code
execution and I do not report it as such. The genuine untrusted input is narrower and real:

- `_nodos.yml` **arrives from a cloned repo or a shared map**. `docs/ARCHITECTURE.md:36` says so in
  the product's own words: *"the payload is file-derived text: attachment values are read out of
  `_nodos.yml`, which is user- or repo-supplied."*
- The operator did not necessarily author the file they are about to open. The realistic story is:
  Javier clones a client's map repo, opens it in `mapper`, presses `↵` on an attachment row whose
  caption reads `acta de cierre.pdf`, and the launcher runs something else.
- Everything below is scored against *that*, not against a server threat model.

---

## 1 · Scope reviewed

| Reviewed | Source |
|---|---|
| Design under review | `PDR-design-proposal.md` §D2 (inspector), §D3 (`mapper/osopen.py`), §2 (fixtures) |
| Requirements | `01-requirements.md` HLR-N01 (LLR-N01.1–.8), HLR-N02 (LLR-N02.1–.5), §2.7 premises, §4 constraints |
| Oracle | `docs/ARCHITECTURE.md` §1 (context/crossings), §2 (`osopen` charter, `widgets` charter), §3 (dependency bans), §4 (interfaces), risk `A-4` |
| Code | `mapper/model.py`, `mapper/store.py`, `mapper/darkside.py`, `mapper/app.py:235-262` & `:1240-1291`, `mapper/widgets/components.py` |
| Not reviewed | `prototypes/**` (CON-6), Inc-1/D1 keymap, Inc-6/D4 undo — no crossing |

**Environment for every probe:** Python 3.12.7, rich 15.0.0, textual 8.2.8, pyyaml 6.0.3, Windows 11.

---

## 2 · Crossing 1 — the OS-handler launch surface (`mapper/osopen.py`)

### 2.1 · Probe method

I implemented PDR §D3's contract **verbatim** — `kind in {url, file}`; for `url` the
`urlsplit(...).scheme` must be in `{http, https}`; for `file` the path is `Path(...).resolve()` and
must `.exists()` — and fed it a battery of hostile targets through a recording launcher. Nothing was
launched. `<== LAUNCHED` means the recording launcher was called, i.e. **the real one would have
been**.

### 2.2 · `kind == "url"` — the scheme check is the right shape

```
target                                               urlsplit.scheme    verdict
'https://example.com/acta.pdf'                       'https'            launched  <== LAUNCHED
'HTTP://example.com'                                 'http'             launched  <== LAUNCHED
'  javascript:alert(1)'                              'javascript'       refused: scheme
'\tjavascript:alert(1)'                              'javascript'       refused: scheme
'java\nscript:alert(1)'                              'javascript'       refused: scheme
'data:text/html,<script>x</script>'                  'data'             refused: scheme
'file:///C:/Windows/System32/calc.exe'               'file'             refused: scheme
'vscode://file/C:/x'                                 'vscode'           refused: scheme
'ms-msdt:/id PCWDiagnostic'                          'ms-msdt'          refused: scheme
'search-ms:query=x&crumb=location:\\evil\share'      'search-ms'        refused: scheme
'\\evil.example.com\share\payload.lnk'               ''                 refused: scheme
'//evil.example.com/share/payload'                   ''                 refused: scheme
'example.com/acta.pdf'                               ''                 refused: scheme
'C:\Windows\System32\calc.exe'                       'c'                refused: scheme
'https://user:pass@evil.example.com/'                'https'            launched  <== LAUNCHED
'https://example.com@evil.example.com/'              'https'            launched  <== LAUNCHED
'https://аpple.com/'                                 'https'            launched  <== LAUNCHED   (cyrillic а)
'http://127.0.0.1:8080/admin/delete'                 'http'             launched  <== LAUNCHED
'https://example.com/‮exe.acta'                      'https'            launched  <== LAUNCHED   (U+202E)
```

**The allowlist refuses the right things, and it refuses them for the right reason.** This is worth
recording precisely, because it is *`urlsplit` doing the work, not the comparison*:

- `urlsplit` **lowercases** the scheme → `HTTP://` normalises to `http`. Case is handled.
- `urlsplit` **strips leading C0 whitespace and removes embedded tab/newline** before parsing →
  `"  javascript:"`, `"\tjavascript:"` and `"java\nscript:"` all yield scheme `javascript` and are
  refused. Whitespace smuggling is handled.
- UNC (`\\host\share`), protocol-relative (`//host/x`) and schemeless (`example.com/x`) all yield
  scheme `''` → refused. A bare Windows path yields scheme `'c'` → refused.

**Therefore the check must be specified as a mechanism, not as an outcome.** A naive implementation
of the same *intent* — `target.startswith("http")`, or `target.split(":")[0]` — flips several rows
above from refused to launched (`target.split(":")[0]` on `"  javascript:alert(1)"` gives
`"  javascript"`, which is not in the allowlist, but on `"HTTP://x"` gives `"HTTP"`, which is also
not in the allowlist — so a case-naive split **breaks the benign case** and a `startswith` check
**admits** `httpx://`). See condition **C-4**.

Residual on the `url` branch: **target/display mismatch** (F-M4). Userinfo confusion, homograph and
RTL-override targets all launch. The inspector shows `Attachment.caption`; the launcher opens
`Attachment.path`; a hostile map controls both independently.

### 2.3 · `kind == "file"` — "the path must exist" is a usability check, not a security control

Stated plainly, as asked: **`.exists()` is a usability control. It is not a security control.** It
answers "will the launch fail?", not "should this launch?". Executed, with workspace
`C:\Users\jjgh8\Github\mapper\maps`:

```
inside workspace              -> resolve='...\mapper\maps\legacy.mmd'                launched  <== LAUNCHED
traversal via ..              -> resolve='C:\Users\jjgh8\.gitconfig'                 launched  <== LAUNCHED
absolute, outside ws, EXISTS  -> resolve='C:\Windows\System32\calc.exe'              launched  <== LAUNCHED
powershell.exe                -> resolve='...\WindowsPowerShell\v1.0\powershell.exe' launched  <== LAUNCHED
NTFS alternate data stream    -> resolve='...\maps\legacy.mmd:$DATA'                 refused: missing
UNC                           -> resolve='\\evil.example.com\share\payload.lnk'      refused: missing
empty string                  -> resolve='C:\Users\jjgh8\Github\mapper'              launched  <== LAUNCHED
"." (a directory)             -> resolve='C:\Users\jjgh8\Github\mapper'              launched  <== LAUNCHED
```

Containment test on the same paths:

```
C:\Windows\System32\calc.exe                    is_relative_to(workspace) = False
C:\Users\jjgh8\Github\mapper\pyproject.toml     is_relative_to(workspace) = False
```

Three things follow.

**(a) `os.startfile` is an execution primitive, by its own documentation.** Probed:

> `os.startfile.__doc__` → *"Start a file with its associated application. When "operation" is not
> specified or "open", this acts like **double-clicking the file in Explorer**, or giving the file
> name as an argument to the DOS "start" command…"*

Double-clicking `payload.exe`, `payload.bat`, `payload.ps1`, `payload.lnk`, `payload.hta`,
`payload.scr`, `payload.msi` or `payload.reg` runs it. There is no shell and no argument string, so
**the PDR is correct that argument injection is foreclosed** — `os.startfile(path)` takes one
positional path, and `subprocess.run(["xdg-open", path])` is a list form with no `shell=True`, so
metacharacters in the path are inert as *shell* metacharacters. That is not the risk. The risk is
that the primitive's whole purpose is "run whatever this file's association says", and the design
lets the file be any file on the disk. Same on POSIX: `xdg-open` on a `.desktop` file executes its
`Exec=` line.

**(b) The two refusals in that table are accidents, not rules.** UNC was refused because
`evil.example.com` is unreachable, so `.exists()` returned False — **on a reachable share it exists
and launches**, and a `.lnk` on a remote share is the classic Windows delivery. The NTFS ADS case
was refused because `resolve()` mangled the `:$DATA` suffix into a non-existent path, not because
any rule named alternate data streams. Neither refusal is something a test could depend on.

**(c) The empty string is not refused.** `Path("").resolve()` is the current working directory,
which exists, so `""` and `"."` both launch an Explorer window on the repo root. Harmless in itself,
but it proves there is no input-shape validation at all in front of the launcher.

### 2.4 · Type confusion — `Attachment.path` is not guaranteed to be a string

`store.py:193` builds `Attachment(kind=a["kind"], path=a["path"], caption=a.get("caption", ""))`
straight out of `yaml.safe_load`, and `model.py:17-22` declares the types but enforces nothing
(a plain `@dataclass(frozen=True)`, no `__post_init__`). Executed against a hand-written sidecar:

```
Attachment(path=12345 type=int)       -> osopen RAISED AttributeError: 'int' object has no attribute 'decode'
Attachment(path={'a': 1} type=dict)   -> osopen RAISED TypeError: argument should be a str or an os.PathLike ... not 'dict'
Attachment(path=[1, 2] type=list)     -> osopen RAISED TypeError: ... not 'list'
attachment entry with no `path:` key  -> store.py:193 construction RAISED KeyError: 'path'
```

Two distinct defects. The `KeyError` kills `MapStore.load` — **a malformed sidecar denies the whole
map**, and the operator gets a traceback rather than a message. The `TypeError`/`AttributeError`
escape a function that PDR §D3 contracts to *return a status word*, so a caller written against that
contract has no handler and the app dies on `↵`.

### 2.5 · What "refuse" must mean

PDR §D3 prose says refused targets are "refused and reported"; the signature returns a status word.
**No LLR requires the caller to surface it.** `LLR-N02.5` says "shall be refused and reported, not
launched" but names no observable surface, and `AT-N02d` is specified as a unit test over `osopen`
— which can pass with the caller dropping the return value on the floor. `docs/ARCHITECTURE.md:287`
(risk A-4) is explicit that acceptance must include "**a visible non-fatal error** for anything
rejected". That is F-M6.

### 2.6 · Signature divergence from the oracle

`docs/ARCHITECTURE.md:147` specifies:

```
open_attachment(target: str, *, workspace: Path) -> None   # raises on non-allowlisted input
```

`PDR-design-proposal.md:87` proposes:

```
open_attachment(att: Attachment, *, launcher=None) -> str
```

The interface is marked *"NO — Inc-4 owns it"*, so it is legitimately in motion and changing its
shape is authorised. Two of the three changes are still defects:

- Taking `Attachment` forces `from mapper.model import Attachment` inside `osopen`, which is banned
  twice: `docs/ARCHITECTURE.md:105` (`osopen → anything in mapper`) and `:66` (*"No `model`, no
  `store`, … no attachment discovery"*). The ban's stated purpose — keep the crossing a one-file
  greppable audit surface, and stop `osopen` discovering its own targets — is exactly the property a
  security reviewer depends on next batch.
- Dropping `workspace` makes confinement **unimplementable inside the boundary module**. This is the
  mechanism by which the blocker exists: it is not that the designer forgot to write "confine", it
  is that the signature has nowhere to put the workspace root.
- Returning a status word instead of raising is fine *if* F-M6's reporting requirement lands.

Adding `launcher` as an injection seam is good and I endorse it (it is what let me run §2.2/§2.3
without launching anything). It needs one guard: see F-m5.

---

## 3 · Crossing 2 — file-derived text into the Rich/Textual render path (C-17)

### 3.1 · Headline: markup is handled, control characters are not

The design's markup discipline is **correct**, and I verified it rather than assuming it. What C-17
does not cover — and what nothing in the batch covers — is raw terminal control characters. The
`Ds*` components are clean. The mandated `Input` widget is clean for markup and **dirty for ANSI**.

### 3.2 · Which sinks parse markup — executed

| Construction | Markup-parsed? | Probe result |
|---|---|---|
| `Text(f" {x} ")` (constructor) | **no** | `.spans=[]`, plain text preserved verbatim |
| `Text.append(x, style=…)` | **no** | `.plain='[bold red on white]OWNED[/]'` — literal |
| `Text.assemble((x, style))` | **no** | `.plain='[bold red on white]OWNED[/]  presupuesto [ok'`, spans are only the explicit styles |
| `Static.update(<str>)` | **YES** | `Content('OWNED', spans=[Span(0, 5, style='bold red on white')])` |
| `Label(<str>)` / `Label.update(<str>)` | **YES** | same; raises on a bad tag (below) |
| `Text.from_markup(x)` | **YES** | `.plain='OWNED'`, span `(0,5,'bold red on white')` |
| `Input(value=<str>)` | **no** | value rendered verbatim in the compositor strip |

So: **the correct control is "never hand file-derived `str` to a markup-parsing sink", not "call
`escape()`".** The prescribed `Text.assemble` construction achieves it. `rich.markup.escape` does
not, for the reason in §3.4.

### 3.3 · A hostile ficha CAN crash the render — proven

```
Static.update('[bold red on white]OWNED[/]')  -> OK, style consumed  (leak)
Static.update('presupuesto [ok')              -> OK (unbalanced OPEN does not raise)
Static.update('[/bold]saldo')                 -> RAISED MarkupError: closing tag '[/bold]' does not match any open tag
Static.update('[on #ff0000]documento')        -> OK (leak)
Label.update('[/bold]saldo')                  -> RAISED MarkupError: closing tag '[/bold]' does not match any open tag
```

Answering the three questions the brief asks, from the probe:

- **Crash the render:** **yes.** A ficha field, title, note, schema label or caption whose value
  begins with an unmatched closing tag — `[/bold]`, `[/]`, `[/i]` — raises `MarkupError` at the
  `.update()` call site. Raised inside a Textual message handler this terminates the app with a
  traceback. Note the asymmetry the probe exposes: an unbalanced **open** bracket (`presupuesto [ok`
  — precisely the PDR §2 fixture) does **not** raise. A fixture that only tests the unbalanced-open
  case would pass while the crashing case ships.
- **Leak a style:** **yes.** `[bold red on white]OWNED[/]` rendered as `OWNED` with the attacker's
  span. `[on #ff0000]documento` renders a red-background label. Under CON-4 (`#1783ff` only on
  interactivity, alert tone reserved for required-empty per LLR-N01.3) a hostile ficha can paint
  itself with the accent or the alert colour and lie about its own coverage state.
- **Spoof chrome:** **yes**, and via the stronger channel in §3.5, not via markup.

### 3.4 · `rich.markup.escape` is the wrong control here — and it is already leaving artifacts

PDR §D2 cites `app.py:1258` and `darkside.py:220` as "the same discipline… the inspector must not
regress". Executed, that discipline is a **no-op for safety and a defect for display**, because both
sites escape into a construction that never parsed markup in the first place:

```
Text.append(raw)       .plain='[bold red on white]OWNED[/]'
Text.append(escape())  .plain='\\[bold red on white]OWNED\\[/]'     <- backslashes are now VISIBLE
```

`darkside.fit()` (`darkside.py:220-227`) escapes and then returns `Text(s).plain`, so the backslash
survives into the returned string *and* is counted against the width budget:

```
fit(title, 30) = '\\[bold red on white]OWNED\\[/] '   len=30
fit(title, 12) = '\\[bold red …'                      len=12   <- 2 of 12 cells are the artifact
```

A hostile title therefore steals display columns from a fixed-width field. Minor on its own, but it
is why **LLR-N01.8 must not offer `rich.markup.escape` as an accepted alternative** — it is the
control that looks right and is not (F-M2, condition C-5).

### 3.5 · The uncovered channel: raw ANSI / OSC reaches the terminal

`rich.markup.escape` does not touch `ESC`, `Text.assemble` does not strip it, and Textual's
compositor carries it through verbatim. Executed:

```
rich.markup.escape('acta \x1b[31mroja\x1b[0m') = 'acta \x1b[31mroja\x1b[0m'   <- unchanged

Static.update(Text.assemble((caption, INK)))
  RAW ESC in compositor strip 4: segment.text='acta \x1b[31mroja\x1b[0m'
  raw ANSI reaches the compositor segment stream: True

Input(value='acta \x1b[31mroja\x1b[0m')     -> strip 1: esc=True '▊  acta \x1b[31mroja\x1b[0m …'
Input(value='acta\x1b[6A\x1b[40Dspoof')     -> strip 4: esc=True '▊  acta\x1b[6A\x1b[40Dspoof …'
```

The compositor segment stream is the last stop before the terminal write. Rendering the same payload
through a Rich console confirms the bytes that would be emitted:

```
cursor-jump      -> emitted bytes: 'acta\x1b[6A\x1b[40Dmapper  guardado ✓'
osc52-clipboard  -> emitted bytes: 'acta\x1b]52;c;cGF5bG9hZA=='
```

**This is the chrome-spoofing answer, and it is not theoretical.** `\x1b[6A\x1b[40D` moves the
cursor up six rows and left forty columns, out of the inspector and into the `TabStrip` / `KeyBar` /
`#map-toast` region, and the following characters overwrite it. A map file can therefore paint a
false "guardado ✓" toast, a false breadcrumb, or a false key hint. `\x1b]52;c;…` is an OSC 52
clipboard write, supported by iTerm2, kitty, foot, and Windows Terminal — a cloned map can silently
replace the operator's clipboard contents. Worst case, and terminal-dependent, are response-inducing
sequences (DSR/DECRQSS), where the terminal writes a reply back onto the application's stdin; for a
TUI that is synthesised keystrokes into a screen that has destructive bindings (`x` archives).

Severity is **blocker** and not more: this needs a hostile or careless map file, the operator is the
only victim, and there is no network amplification. But "the operator cloned a client's map" is the
documented normal case for this product, and the fix is small.

**A candidate control, executed against every payload** (this is a recommendation, not applied code):

```python
import re
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")

def safe(s) -> str:
    """Coerce to str and neutralise terminal control characters."""
    if not isinstance(s, str):
        s = str(s)
    return _CTRL.sub("\ufffd", s)
```

```
markup           safe()='[bold red on white]OWNED[/]'      residual ESC in output: False
closer           safe()='[/bold]saldo'                     residual ESC in output: False
ansi             safe()='acta �[31mroja�[0m'               residual ESC in output: False
cursor-jump      safe()='acta�[6A�[40Dmapper  guardado ✓'  residual ESC in output: False
osc52-clipboard  safe()='acta�]52;c;cGF5bG9hZA==�'         residual ESC in output: False
int (yaml)       safe()='12345'                            residual ESC in output: False
None             safe()='None'                             residual ESC in output: False
```

It closes the ANSI channel and the §2.4 type-confusion channel in the same three lines, and it
preserves `\n`/`\t` so notes keep their line breaks.

### 3.6 · The `Ds*` components are clean — probed individually

The brief asks specifically about `DsChip`, `DsTextField` and `DsSegmented`, which build
`Text(f" {...} ")` from caller strings. All three are safe, because the `Text(...)` **constructor**
does not parse markup:

```
DsChip(label='[bold red on white]OWNED[/]').render()
  type=Text  .plain=' [bold red on white]OWNED[/] '  .spans=[]
  (live, mounted in an app: identical — .spans=[])

DsTextField(value='[bold red on white]OWNED[/]').render()
  .plain=' [bold red on white]OWNED[/] '  spans=[]

DsSegmented(options=['ok','[blink]riesgo[/]','tarde']).render()
  .plain=' ok   [blink]riesgo[/]   tarde '
  .spans=[(0,4,'bold #000000 on #1783ff'), (5,23,'#737373 on #262626'), (24,31,'#737373 on #262626')]
```

`.spans=[]` on `DsChip` is the load-bearing result: no attacker-controlled span was created, and the
only style applied is the component's own. **No `Ds*` component interpolates a caller string into a
markup-parsed path.** They remain vulnerable to the §3.5 control-character channel like every other
renderable, which the `safe()` coercion at the inspector boundary closes without touching them.

### 3.7 · Enumeration gap in the file-derived inventory

PDR §D2 lists the inspector's untrusted inputs as "titles, notes, field values, attachment
captions". The following are equally file-derived and are omitted from both the design sentence and
the PDR §2 hostile fixture:

| Omitted input | Where it enters | Where it renders |
|---|---|---|
| `SchemaField.label` | `store.py:158-166`, from `sidecar["schema"]` | **the inspector row label itself** (LLR-N01.2) |
| `SchemaField.key` | same | row identity, `#`-ids if derived from it |
| `Ficha.state` | `store.py:187` | `DsSegmented` active option (D2) |
| `Ficha.meta` | `store.py:188` | ficha header (`app.py:1261`) |
| `Attachment.path` | `store.py:193` | chip label when `caption` is empty (`app.py:259`) |
| `node.id` | mermaid `.mmd` source | title fallback (`app.py:1258`), crumb |
| `Edge.label`, `Document.*` | `mermaid.parse`, `store.py:168-180` | rail / doc surfaces |

The schema label is the sharpest one: LLR-N01.2 **requires** the row to be labelled from
`SchemaField.label`, so the batch is deliberately routing a new piece of file-derived text into a
new render site, and neither the markup sentence nor the fixture mentions it.

---

## 4 · Findings

### Blockers

#### F-B1 — `kind == "file"` launches anything on the disk; the mandated workspace confinement is absent · **blocker**

- **Attack.** A cloned or shared map ships `_nodos.yml` with
  `attachments: [{kind: file, path: "..\\..\\..\\payload.lnk", caption: "acta de cierre.pdf"}]`.
  The inspector shows the caption; `↵` hands the resolved path to `os.startfile`, which by its own
  documentation "acts like double-clicking the file in Explorer". `.exe`, `.lnk`, `.bat`, `.ps1`,
  `.hta`, `.scr`, `.msi`, `.reg` execute. On POSIX, `xdg-open` on a `.desktop` file runs its `Exec=`.
- **Where.** `PDR-design-proposal.md:94-96` (§D3, `file` branch) and `01-requirements.md:108-109`
  (LLR-N02.4/.5), against `docs/ARCHITECTURE.md:36`, `:147`, `:287`.
- **Evidence.** §2.3 — traversal via `..` resolved to `C:\Users\jjgh8\.gitconfig` and launched;
  `C:\Windows\System32\calc.exe` launched; `powershell.exe` launched. `is_relative_to(workspace)`
  is `False` for both and is never consulted, because the signature has no `workspace`.
- **Why it matters.** `docs/ARCHITECTURE.md:36` already requires "path confinement under the
  workspace for `file`" and calls this "the highest-risk crossing in the system". Risk `A-4`
  (`:287`) names it as the batch's real attack surface and makes `security-reviewer` sign-off a
  gate. The design silently drops the control; no LLR restates it; so nothing in the batch would
  catch its absence.
- **Note on what is NOT wrong.** Shell/argument injection **is** foreclosed as the PDR claims:
  `os.startfile(path)` is a single positional path with no command line, and
  `subprocess.run(["xdg-open", path])` is the list form with no `shell=True`. I verified there is no
  `shell=True` anywhere in `mapper/` (only `diff.py:36` and `github.py:46,145,248`, all list-form).
  The blocker is the *choice of target*, not the *construction of a command*.
- **Closes with.** Conditions **C-1**, **C-2**, **C-3**.

#### F-B2 — Terminal control characters from `_nodos.yml` reach the terminal; C-17 covers only markup · **blocker**

- **Attack.** A caption/title/note/label containing `\x1b[6A\x1b[40D…` repositions the cursor out of
  the inspector and overwrites `TabStrip` / `KeyBar` / `#map-toast` — a forged "guardado ✓" or a
  forged breadcrumb. `\x1b]52;c;<base64>\x07` writes the operator's clipboard on iTerm2, kitty, foot
  and Windows Terminal. Response-inducing sequences can, terminal-dependent, push bytes back onto
  stdin of a screen whose `x` binding archives a subtree.
- **Where.** `PDR-design-proposal.md:80-82` (§D2 markup-safety, scoped to markup only) and
  `01-requirements.md:90` (LLR-N01.8, same scope). Render sites: every inspector row, plus
  `Input(value=…)` mandated by LLR-N01.5.
- **Evidence.** §3.5 — `raw ANSI reaches the compositor segment stream: True` from
  `Static.update(Text.assemble(...))`; `Input(value=…)` strips show `esc=True` for both a colour
  payload and a cursor-jump payload; Rich emits `'acta\x1b[6A\x1b[40Dmapper  guardado ✓'` and
  `'acta\x1b]52;c;cGF5bG9hZA=='` verbatim. `rich.markup.escape` leaves `ESC` unchanged.
- **Why it matters.** The batch's own hostile fixture (`PDR-design-proposal.md:142`) specifies "an
  attachment caption containing an ANSI escape", so `AT-N01e` is written to exercise a channel that
  no control in the design addresses. Either the test fails at Inc-2, or — worse — it is written to
  assert only the markup half and passes vacuously while the channel ships open.
- **Closes with.** Conditions **C-6**, **C-7**.

### Majors

#### F-M1 — `open_attachment` signature diverges from the architecture oracle and forces a banned import · **major**
- **Where.** `PDR-design-proposal.md:87` vs `docs/ARCHITECTURE.md:147`.
- **What.** Taking `att: Attachment` forces `from mapper.model import …` inside `osopen`, banned at
  `docs/ARCHITECTURE.md:105` (`osopen → anything in mapper`) and `:66`. Dropping `workspace` is the
  mechanism of F-B1. Returning a status word instead of raising is acceptable only with F-M6.
- **Why it matters.** The ban exists so the crossing stays a one-file greppable audit surface and so
  `osopen` cannot discover its own targets. Breaking it costs the next reviewer the property this
  review depended on.
- **Closes with.** **C-1** (which restores the oracle's signature) and **C-9**.

#### F-M2 — LLR-N01.8 mandates a control that is a no-op in the prescribed construction · **major**
- **Where.** `01-requirements.md:90`; existing sites `app.py:1258`, `app.py:239-259`,
  `darkside.py:220-227`, `darkside.py:88,129,154`.
- **What.** LLR-N01.8 accepts `rich.markup.escape` as an alternative to `Text.assemble`. §3.4 proves
  `Text.append`/`Text.assemble` never parse markup, so `escape()` there protects nothing and injects
  visible `\[` artifacts. The real invariant is the *sink*, not the escape.
- **Evidence.** §3.4 — `Text.append(escape()).plain='\\[bold red on white]OWNED\\[/]'`.
- **Closes with.** **C-5**.

#### F-M3 — the file-derived inventory omits schema labels, `state`, `meta`, `path` and `node.id` · **major**
- **Where.** `PDR-design-proposal.md:80-82` and `:142` (fixture); inputs enumerated in §3.7.
- **What.** LLR-N01.2 deliberately routes `SchemaField.label` — read from `sidecar["schema"]` at
  `store.py:158-166` — into a brand-new render site, and neither the markup sentence nor the hostile
  fixture covers it. Same for `Ficha.state` into `DsSegmented`, `Attachment.path` into the chip
  fallback (`app.py:259`), and `node.id` into the title fallback (`app.py:1258`).
- **Closes with.** **C-8**.

#### F-M4 — URL target/display mismatch: userinfo, homograph and RTL-override targets launch · **major**
- **Where.** `PDR-design-proposal.md:92-93`; `01-requirements.md:109` (LLR-N02.5).
- **Evidence.** §2.2 — `https://user:pass@evil.example.com/`,
  `https://example.com@evil.example.com/`, `https://аpple.com/` (Cyrillic `а`) and
  `https://example.com/‮exe.acta` (U+202E) all launched.
- **Why it matters.** The operator reads `Attachment.caption`; the launcher opens `Attachment.path`;
  a hostile map controls both independently. Credential-bearing URLs are also handed to the browser
  and land in its history. Not a blocker — the browser is the thing that opens, and the operator can
  still bail — but the inspector is currently designed to *hide* the discrepancy.
- **Closes with.** **C-10**, **C-11**.

#### F-M5 — malformed or non-string sidecar values crash `load` and escape `osopen`'s contract · **major**
- **Where.** `store.py:193`; `model.py:17-22`; `PDR-design-proposal.md:87`.
- **Evidence.** §2.4 — missing `path:` key → `KeyError: 'path'` out of `MapStore.load` (the whole
  map is denied); `path: 12345` → `AttributeError: 'int' object has no attribute 'decode'` raised
  *from inside* a function contracted to return a status word; `path: {a: 1}` / `[1,2]` →
  `TypeError`.
- **Closes with.** **C-3** (osopen-side coercion) and **C-12** (store-side tolerance).

#### F-M6 — nothing requires a refusal to be visible to the operator · **major**
- **Where.** `01-requirements.md:109` (LLR-N02.5 — "refused and reported", no surface named);
  `AT-N02d` is specified as a unit test over `osopen`.
- **What.** A status-word return that the caller discards is a silent no-op, which the brief and
  `docs/ARCHITECTURE.md:287` both forbid ("a visible non-fatal error for anything rejected").
- **Closes with.** **C-13**.

### Minors

| id | Finding | Where | Evidence / note |
|---|---|---|---|
| F-m1 | `darkside.fit` leaks escape backslashes into plain text and charges them to the width budget | `darkside.py:220-227` | `fit(title,12)='\\[bold red …'` — 2 of 12 cells are artifact |
| F-m2 | UNC and NTFS-ADS `file` targets are refused **by accident** (unreachable host / `resolve()` mangling), not by any rule | §2.3 | a reachable share exists → launches; no test can depend on today's behaviour |
| F-m3 | empty-string and directory `file` targets launch (Explorer on the repo root) | §2.3 | `Path("").resolve()` = CWD, which exists |
| F-m4 | `yaml.safe_load` does not bound alias expansion | `store.py:206` | probed: **239 input bytes → 262,144 expanded leaves in 2 ms**; `safe_load` blocks object construction, not amplification |
| F-m5 | `launcher=None` default must not be allowed to become a silent no-op | `PDR-design-proposal.md:87` | a seam that defaults to "do nothing" makes `AT-N02c` pass and the feature dead |
| F-m6 | no stated policy on executable/script extensions even inside the workspace | §D3 | a `payload.lnk` committed *into* the map folder passes confinement |

---

## 5 · Conditions of approval

Each is individually dischargeable. Paste as-is into `01-requirements.md` §3 under the named HLR,
and record them in §6.5 (Requirement amendments).

### Closing F-B1 + F-M1

> **C-1 · LLR-N02.6** — `open_attachment` **shall** expose the signature
> `open_attachment(kind: str, target: str, *, workspace: Path, launcher=None) -> str`, taking the
> attachment's kind and target as plain strings, and **shall not** import any module from the
> `mapper` package.
> *Verification:* test (unit) — `inspect.signature`; plus an AST/import census over `mapper/osopen.py`
> asserting zero `mapper.*` imports.

> **C-2 · LLR-N02.7** — For `kind == "file"`, `open_attachment` **shall** resolve the target with
> `Path(target).resolve()` and **shall** refuse any target for which
> `resolved.is_relative_to(workspace.resolve())` is false, before any launcher is called. Refusal
> **shall** apply irrespective of whether the target exists, and existence **shall not** be treated
> as an authorisation.
> *Verification:* test (unit) — `AT-N02d` extended to a table of at least: a path inside the
> workspace (launched); a `..`-traversal escaping it (refused); an absolute path outside it that
> exists (refused); a UNC path `\\host\share\x` (refused); an empty string (refused); a directory
> (refused); a path bearing an NTFS alternate data stream `file:stream` (refused). Threshold: 100 %
> of the table, with the launcher asserted **not** called on every refusal row.

> **C-3 · LLR-N02.8** — `open_attachment` **shall** refuse, without calling the launcher, any target
> that is not a non-empty `str`, and **shall not** raise for any input reachable from a
> `yaml.safe_load` of `_nodos.yml`; it **shall** return a refusal status word instead.
> *Verification:* test (unit) — inputs `12345`, `{"a": 1}`, `[1, 2]`, `None`, `""` each return a
> refusal status and leave the recording launcher's call count at 0.

### Closing the `url` branch (F-M4) and locking the mechanism

> **C-4 · LLR-N02.9** — For `kind == "url"`, the scheme test **shall** be performed on
> `urllib.parse.urlsplit(target).scheme` compared against the exact lowercase set `{"http", "https"}`.
> Prefix matching (`startswith`) and manual splitting on `":"` **shall not** be used.
> *Verification:* test (unit) — the §2.2 table as a parametrised case list; `HTTP://example.com`
> launches, and `javascript:`, `data:`, `file:`, `vscode:`, `ms-msdt:`, `search-ms:`, a UNC path, a
> protocol-relative `//host/x`, a schemeless `example.com/x` and a bare `C:\…` path are all refused.

> **C-10 · LLR-N02.10** — For `kind == "url"`, `open_attachment` **shall** refuse any target whose
> parsed authority contains userinfo (an `@` before the host).
> *Verification:* test (unit) — `https://user:pass@evil.example.com/` and
> `https://example.com@evil.example.com/` are refused, launcher call count 0.

> **C-11 · LLR-N02.11** — The inspector **shall** display the attachment's resolved target alongside
> its caption, so that the string the operator reads is the string the launcher receives; where the
> two differ the target **shall** be the one shown in full.
> *Verification:* test (pilot) — a fixture attachment whose `caption` is `"acta de cierre.pdf"` and
> whose `path` is `"https://evil.example.com/x"` renders the host in the inspector.

### Closing F-B2 and the markup findings

> **C-6 · LLR-N01.9** — Every value the inspector renders that originates from `_nodos.yml` or the
> `.mmd` source **shall** pass through a single coercion helper that (a) converts non-`str` values
> to `str` and (b) replaces every C0/C1 control character other than `\n` and `\t` with U+FFFD,
> before it is placed in any renderable or in an `Input.value`.
> *Verification:* test (unit) over the helper — payloads `"\x1b[31m"`, `"\x1b[6A\x1b[40D"`,
> `"\x1b]52;c;cGF5bG9hZA==\x07"`, `12345`, `None`; plus test (pilot) — after mounting a node whose
> title, notes, schema label and attachment caption each carry one of those payloads, no strip
> returned by the screen compositor contains `\x1b`.

> **C-7 · LLR-N01.10** — No inspector code path **shall** pass a file-derived `str` to a
> markup-parsing sink (`Static.update(str)`, `Label(str)`, `Label.update(str)`,
> `Text.from_markup`, `Console.print(str)`). File-derived text **shall** reach the screen only
> inside a `rich.Text` built by `Text.assemble` / `Text.append` with explicit styles, or as an
> `Input.value`.
> *Verification:* test (pilot) — `AT-N01e` extended so that a ficha field whose value is
> `"[/bold]saldo"` renders without raising `MarkupError`, **and** a title of
> `"[bold red on white]OWNED[/]"` appears in the rendered strip with its brackets intact and with no
> span carrying a style the inspector did not set.

> **C-5 · amend LLR-N01.8** — replace "constructed with explicit styles (`Text.assemble` /
> `rich.markup.escape`)" with "constructed with explicit styles via `Text.assemble` / `Text.append`;
> `rich.markup.escape` **shall not** be used as the control, because those constructions do not
> parse markup and escaping into them emits literal backslashes."
> *Verification:* test (unit) — a census over `mapper/widgets/inspector.py` asserting zero calls to
> `rich.markup.escape`.

> **C-8 · amend the PDR §2 hostile fixture and LLR-N01.8's input set** — the hostile-text fixture
> **shall** carry a hostile value in each of: `Ficha.title`, `Ficha.notes`, `Ficha.state`,
> `Ficha.meta`, a `SchemaField.label`, a schema field value, `Attachment.caption`, `Attachment.path`
> and a `node.id`; and **shall** include all three payload classes — an unbalanced **opening**
> bracket, an unmatched **closing** tag, and a control-character sequence.
> *Verification:* the fixture's own assertions; `AT-N01e` iterates the full set.

### Closing F-M5, F-M6, F-m5

> **C-12 · LLR-N02.12** — `MapStore.load` **shall not** raise on a sidecar whose `attachments`
> entries are malformed; an entry lacking `kind` or `path`, or that is not a mapping, **shall** be
> skipped and counted, and the map **shall** load.
> *Verification:* test (unit) — a sidecar with one valid and three malformed attachment entries
> loads, yields exactly one `Attachment`, and reports 3 skipped.

> **C-13 · LLR-N02.13** — When `open_attachment` returns a refusal, the caller **shall** surface a
> visible, non-fatal message to the operator naming the reason; a refusal **shall not** result in no
> observable change.
> *Verification:* test (pilot) — `AT-N02d` promoted from unit to pilot: activating an attachment
> with `path: "javascript:alert(1)"` produces an observable notification/toast, the graph is
> unchanged, and the app does not exit.

> **C-14 · LLR-N02.14** — Only `mapper/app.py` **shall** call `open_attachment`; the inspector widget
> **shall** emit a Textual `Message` and **shall not** import `mapper.osopen`.
> *Verification:* test (unit) — import census over `mapper/widgets/` asserting zero `osopen`
> references. (This restates the standing ban at `docs/ARCHITECTURE.md:95` and `:105`; it is listed
> as a condition because Inc-4's file set contains both `mapper/widgets/inspector.py` and
> `mapper/app.py`, which is exactly when the ban gets crossed by convenience.)

> **C-15 · LLR-N02.15** — `open_attachment`'s `launcher` parameter, when not supplied, **shall**
> default to the real platform launcher; it **shall not** default to a no-op.
> *Verification:* test (unit) — with `launcher` omitted and the platform call monkeypatched, the
> platform call is made exactly once for a permitted target.

### Recommended, not blocking

> **C-16 (minor, F-m6)** — record in `docs/ARCHITECTURE.md` §1 whether extensions that execute on
> open (`.exe .lnk .bat .cmd .ps1 .hta .scr .msi .reg .js .vbs .jar .desktop`) are refused even
> inside the workspace. My recommendation is to refuse them and report; a map folder is not a
> trust boundary against a repo you cloned. If they are permitted, say so explicitly so the next
> reviewer reads a decision rather than an omission.

> **C-17 (minor, F-m1)** — fix `darkside.fit` to stop escaping (`darkside.py:221`), since it returns
> `.plain` into non-markup constructions. Touches a `design`-module function with four consumers;
> if that widens a lane, defer it and record it — but the width miscount is real.

> **C-18 (minor, F-m4)** — note the `yaml.safe_load` amplification property in
> `docs/ARCHITECTURE.md` §1's filesystem row. No code change requested this batch.

### Amendment needed to the oracle

`docs/ARCHITECTURE.md:36` lists the scheme allowlist as `http`/`https`/**`file`**. The PDR narrows
`kind == "url"` to `http`/`https` and routes local files through `kind == "file"` instead. That is a
**narrowing, i.e. the safe direction**, and I endorse it — but the oracle and the design must not
disagree in writing on a control this batch is being gated on. Amend row `OS default apps` to read:
*"scheme allowlist `http`/`https` for `kind == "url"`; `file:` URLs refused; local files reached
only through `kind == "file"`, confined under the workspace root; no shell."*

---

## 6 · Evidence checklist

| Item | ✓/✗ | Evidence |
|---|---|---|
| Each finding has what · where · why · recommendation | ✓ | §4 — every F-B/F-M carries all four; minors carry where + evidence and map to a numbered condition |
| Each finding has a severity rating | ✓ | 2 `blocker`, 6 `major`, 6 `minor` — §4 headings and the minors table |
| No secret values appear in this output | ✓ | No credential, token or key was read or emitted. `C:\Users\jjgh8\.gitconfig` appears as a **resolved path** in probe output — its contents were never read |
| Verdict is explicit | ✓ | §0 — `approved with conditions` |
| New tool/integration: scope and blast radius addressed | ✓ | §2 — `osopen` is the new external-action surface. Scope: OS default-application launch. Blast radius as designed: **any file on the operator's disk, executed by association** (§2.3, probed). Reversibility: none — a launch cannot be undone. Human-in-the-loop: the `↵` keystroke is the approval, which is why target/display honesty (C-11) matters. Data flow: for `kind == "url"`, the target host learns the operator's IP and any userinfo embedded by the map author — flag for LFPDPPP where a client map is involved |
| Findings backed by an executed probe rather than reasoning | ✓ | §2.2, §2.3, §2.4 (osopen contract, verbatim, recording launcher) · §3.2, §3.3, §3.4, §3.5, §3.6 (markup/ANSI sinks under textual 8.2.8) · F-m4 (yaml amplification) |
| No code changed; `prototypes/` untouched | ✓ | Probes ran from the session scratchpad against the installed package; no file under `C:\Users\jjgh8\Github\mapper\mapper\` or `prototypes\` was written |

### Probe scripts

Retained in the session scratchpad, not added to the repo:

- `…\scratchpad\probe_markup.py` — Rich-level sinks, `escape()` behaviour, `darkside.fit`, ANSI passthrough
- `…\scratchpad\probe_textual.py` — Textual sinks, `MarkupError`, compositor segment stream
- `…\scratchpad\probe_input.py` — `Input` sink, candidate `safe()` sanitiser, emitted control bytes
- `…\scratchpad\probe_osopen.py` — PDR §D3 verbatim, url/file attack tables, type confusion

---

## 7 · Gate verdict

**`approved with conditions`.**

- **C-1, C-2, C-3, C-6, C-7** discharge the two blockers and **must land before Inc-4 (osopen /
  attachments) and Inc-2 (inspector) merge.**
- **C-4, C-5, C-8, C-10, C-11, C-12, C-13, C-14, C-15** discharge the majors and are due within the
  same increments.
- **C-16, C-17, C-18** are recommendations; they do not gate.

`security-reviewer` re-reads `mapper/osopen.py` and `mapper/widgets/inspector.py` at the Inc-4 gate
before sign-off, per `docs/ARCHITECTURE.md:287` (risk A-4).
