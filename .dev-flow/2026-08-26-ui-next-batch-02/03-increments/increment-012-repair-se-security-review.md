# Increment 012 — Inc-REPAIR S-E — independent security review

**Range:** `git diff fdbdd62..46075a4 -- mapper/ tests/`
**Reviewer:** security-reviewer (gate 2 of 2; code review at
`increment-012-repair-se-code-review.md` returned BLOCK on 3 HIGH, all folded at `46075a4`)
**Date:** 2026-09-11

## VERDICT: **BLOCK** — 2 HIGH

The code review's HIGH-1 is **closed, and I verified it by firing rather than by reading** — the
shipped `Text(darkside.plain(...))` neutralises every markup class I could reach, including two the
code review did not name. That part of the stage is sound and the coercion posture at the render
sinks is a clear **gain** over `fdbdd62`.

The block is elsewhere:

- **SEC-H1 (in-diff).** The `B-48` fix added `store.py:246`, an eleventh unbounded warning producer,
  inside a loop over a YAML list. **Fired: a 220 KB sidecar yields 2.0 GB of load warnings in
  0.84 s — 9,092× amplification** — which is *larger and 60× cheaper* than the alias bomb
  `LLR-N13.1.7` was opened for. The stage that repairs the materialising-diagnostic class shipped a
  new instance of it.
- **SEC-H2 (out-of-diff, found by the census this brief commissioned).** A sidecar ficha title
  reaches the **archive confirmation dialog** as a bare `str` (`app.py:3342` → `app.py:253`).
  Textual markup is parsed there, and `[@click=…]` is executable. **Fired: one mouse click on the
  node name returns `True` from `_ConfirmScreen` — the destructive action is confirmed without the
  operator pressing `y`.** Human-in-the-loop is defeated by file-derived content.

---

## Boundary statement

**I was the sole agent touching this tree.** Working tree clean at `46075a4` on entry and on exit.
No evidence of another writer.

**Mutations.** One (`M-SEC-1`, fired twice). Byte-level against a **CRLF** anchor with the match
count asserted `== 1` before firing; `__pycache__` purged before and after; restored unconditionally
in a `finally`; sha256 verified equal after each. `mapper/screens/coverage.py` pristine and final:
`374779563fbc3987…`. `mapper/store.py` never mutated: `f247d0158c782b7a…`.
`tests/test_repair_sidecar.py` `1cfe5646c2f36918…`, `tests/test_darkside_census.py`
`1db89d08348313879…` — both untouched. No mutating git commands. Scratch in `C:\Users\jjgh8\clde\secrev\`.

**Fired** (11 probes, all reproducible from the scratch scripts):
`p1_markup.py` (9 markup classes × 3 call forms, + OSC-8 emission over 7 URI schemes),
`p2_endtoend.py` (real `CoverageScreen` under Pilot), `m_sec1.py` / `m_sec1_suite.py` (the mutant),
`p4_confirm.py` (`_ConfirmScreen` markup), `p5_static.py` (Textual-markup grammar + a live click),
`p6_confirm_bypass.py` (the confirmation bypass), `p7_bound.py` / `p8b_owner.py` / `p11_attr.py`
(amplification), `p9_truncation.py` (14 hostile payload classes through the truncate→toast
pipeline), `p10_forge.py` (record forgery + two number spot-checks).

**Reasoned about, not fired.** Whether the operator's terminal emulator actions the OSC-8 sequence
(see "could not determine"). Whether a 2 GB toast body kills a live `App.notify` — I measured the
2 GB in the `Graph` and 1.3 s in `darkside.plain`, and stopped there rather than drive a live
notification. Whether Textual's action parser can reach arbitrary Python from `[@click=…]` — I
bound my claim to "any declared action with literal arguments", which is what I observed.

**No secret value appears in this report.** The hostile fixtures are synthetic; the one payload that
names a private path (`file:///C:/Users/OP/.ssh/id_rsa`) is a string I constructed, not a value read
from disk. Hostile code points are named as `U+XXXX` per `C-56` and never pasted.

**Could not determine.**
1. Whether the operator's terminal makes the emitted OSC-8 hyperlink clickable. Windows Terminal,
   WezTerm, iTerm2, kitty and VS Code's integrated terminal all implement OSC-8; I could not test
   the live emulator from a headless session. **This does not change any verdict** — SEC-H2 is
   emulator-independent, and SEC-H1 is a resource bound.
2. Whether `app.py:253` / `app.py:3342` were deliberately deferred. Nothing I read records a
   deferral, and `LLR-N06.2.5` ratifies the *derived-census* discipline for `notify` only.

**Suite, and how much I weight it.** `46075a4` baseline: **997 passed, 19 deselected, 3 xfailed in
261.32 s** (the code review measured 995/20/3 at `ea5d4c2`; the two folded arms account for the
delta). This lane contains the named `FLAKE-1` (`_focus_owner` axis, `state.json` → `named_flakes`),
so **it is a weaker green than the count suggests** and I have not used it as evidence for anything
positive. I use it in exactly one direction — to show that a mutant it *should* redden does not
(SEC-M1) — which is a claim a flaky lane can only strengthen, never weaken.

---

## HIGH findings

### SEC-H1 — the `B-48` fix added the highest-amplification line in the module

**Severity: HIGH.** **Where:** `mapper/store.py:246` (added by this diff) and its pre-existing
sibling `mapper/store.py:251`, both inside `_mappings`' loop over `entries`.

```python
graph.load_warnings.append(f"adjunto sin campos: {owner}.{key}[{i}]")   # :246, NEW
graph.load_warnings.append(f"campo ilegible: {owner}.{key}[{i}]")       # :251, pre-existing
```

**What.** `owner` is the node id — a coerced `str` of unbounded length — and the loop runs once per
element of a YAML **list**, whose elements can each be a 5-byte alias. Neither half is routed
through `_raw_origin`, so the length bound this very stage introduced does not apply.

**Fired** (`p8b_owner.py`, `p11_attr.py`; node id 100,000 chars, `attachments: [*bad, *bad, …]`
where `&bad` is `{z: 1}`):

```
  10 x *bad    file=  100,129 B  load=0.052s  warn_chars=    1,100,387   AMP=    11x
 200 x *bad    file=  101,269 B  load=0.063s  warn_chars=   20,107,707   AMP=   199x
2000 x *bad    file=  112,069 B  load=0.130s  warn_chars=  200,178,907   AMP= 1,786x
20000 x *bad   file=  220,069 B  load=0.840s  warn_chars=2,000,908,907   AMP= 9,092x   plain()=1.29s
```

Attribution at the 200-alias point (`p11_attr.py`): `adjunto sin campos` contributes **20,007,290 of
the 20,107,707 characters — 99.5%**. This is the new line, not its neighbour.

**Why it matters.** Three things make it worse than the bomb `LLR-N13.1.7` was opened for.

1. **It is bigger.** 2.0 GB against the alias bomb's 5.2 GB at nine levels — same order, from a
   220 KB file instead of a deeply-nested one.
2. **It is ~60× cheaper.** 0.84 s against 54 s. *Nothing times out and nothing looks wrong* —
   the operator opens a client's map and the process is simply gone.
3. **The sink is live.** `app.py:548` and `app.py:1287` do
   `darkside.plain("; ".join(graph.load_warnings))` into `self.notify(...)`. I measured
   `darkside.plain` alone at **1.29 s** on the 2 GB join — a per-character `translate` over two
   gigabytes, after the join has already allocated them, on the UI thread.

Both inputs are nearly free in the file: the id costs its length **once**, each additional record
costs **5 bytes**. Amplification is `O(id_len × alias_count)` and unbounded.

This is a realistic delivery shape for this practice: a `_nodos.yml` received from a client or pulled
from a shared repo. The attacker needs no execution, only that the operator open the map.

**Why HIGH.** Resource exhaustion is not on my generic HIGH list, so I am naming the basis
explicitly rather than leaning on the rubric: `LLR-N13.1.7` is a **ratified threshold** of this
batch, it defines this exact class as blocking, and this diff ships a new instance of it that is
26× worse and 60× cheaper than the one the threshold was written for — inside the stage whose
subject is that class. A defect the project has already ruled blocking does not become MEDIUM by
appearing on a different line.

**Smallest fix.** Bound at the sink, which covers all eleven producers and any twelfth — prefer this
over routing two more call sites through `_raw_origin`:

```python
# mapper/app.py:548 and :1287 -- one helper, both sites
_TOAST_CHARS = 2_000
def _warning_toast(warnings: list[str]) -> str:
    body = "; ".join(warnings[:20])
    extra = len(warnings) - 20
    if extra > 0:
        body += f"; … y {extra} avisos más"
    return darkside.plain(body[:_TOAST_CHARS])
```

and, so the 2 GB is never built in the first place, cap the list where it is appended:

```python
# mapper/store.py -- one guard at the top of every append site, or in a helper
_MAX_WARNINGS = 200
def _warn(graph: Graph, message: str) -> None:
    if len(graph.load_warnings) < _MAX_WARNINGS:
        graph.load_warnings.append(message[:300])
```

**Arm.** The module already owns the right oracle — `test_repair_sidecar.py:283`'s `total < 2_000`.
It is the **fixture** that is missing, exactly as it was for the code review's HIGH-2. Add
`attachment_amplified()` (100k id × 200 aliases) and drive the same bound. Measured on the shipped
tree: **20,107,707 joined characters against a 2,000 bound — ~10,000×, deterministic, 0.063 s**
(the arm's `sum(len(w) for w in ...)` differs from the joined length only by the 400 separator
characters). Note the fixture must stay at 200 aliases, not 20,000: at 20,000 the arm allocates
2 GB and is a memory hazard in CI, which is itself a restatement of the finding.

---

### SEC-H2 — a ficha title can confirm its own archive with one click

**Severity: HIGH.** **Where:** `mapper/app.py:3342` (`name = node.ficha.title or node.id` — raw)
→ `:3357/:3361/:3363` (interpolated into `message`) → `mapper/app.py:253`
(`Static(self.message, id="confirm-label")` — a bare `str`).

**Out of the S-E diff.** I report it because this brief commissioned the census
(*"is this the ONLY such sink?"*), and because it is the same rule the diff's own comment states:
*"Safety from markup comes from never handing a file-derived `str` to a markup-parsing sink."*

**What.** `Static` renders a `str` through **Textual's** markup (`textual.content.Content.from_markup`),
not Rich's — a *different, wider* grammar that the batch has not modelled. It accepts
`[@click=<action>]`, which binds a runnable Textual action to the span.

Note `app.py:3335` two lines above **does** call `darkside.plain(node.ficha.title or node.id)` for
the event toast. `:3342` builds the same value again, raw, for the confirmation.

**Fired** (`p6_confirm_bypass.py`, real `_ConfirmScreen` under Pilot, one `pilot.click` on the label):

```
title = "[@click=screen.confirm]Acta[/][conceal]"
  rendered text the operator sees: '¿archivar la raíz «Acta» y sus 8 descendientes? esto reemplazará la raíz del mapa.'
  callback value after ONE click on the node name: True      <-- ARCHIVE CONFIRMED
title = "[@click=app.quit]Acta[/][conceal]"
  app still running: False                                    <-- app terminated
title = "Acta"   (control)
  callback value after ONE click: '<no callback>'             <-- clean
```

The rendered sentence is **identical to the benign one**. The markup is invisible; the payload is
not in the text the operator reads.

**Three distinct impacts, all fired.**

| | Payload | Effect |
|---|---|---|
| a | `[@click=screen.confirm]` | One click on the node name **dismisses the dialog with `True`** — the subtree is archived without `y`. Reachability is namespace-qualified: I fired `screen.confirm` and `app.quit` and both ran; an unqualified `[@click=confirm]` did **not** resolve. `mapper/` declares **62 distinct `action_*` names**, so the qualified surface includes `archive`, `save`, `remove_attachment`, `import_office`, `export_svg`, `undo`. |
| b | `[conceal]` / `[#000000 on #000000]` | Span measured at `(23, 82)` — it covers *"y sus 8 descendientes? esto reemplazará la raíz del mapa"*. The operator approves a subtree deletion believing it is one node. |
| c | `Acta[/]` or `[link=http://…]` | `MarkupError` out of `Screen._refresh_layout` → **the app dies**. Un-catchable by the caller; it is the compositor's own reflow. |

(a) is the one that matters: **the system stops enforcing the human-in-the-loop, and the human cannot
see that it stopped.** My standing rule is that a destructive action must be approved per call by the
operator; here the file being inspected supplies the approval.

**Smallest fix.** Two lines, matching what `coverage.py:113` now does:

```python
# app.py:3342
name = darkside.plain(node.ficha.title or node.id)
# app.py:253
Static(Text(self.message), id="confirm-label"),
```

`plain` alone is **not** sufficient — it does not touch `[`, and `@click` needs no control byte.
`Text(...)` alone is sufficient for markup but leaves the control-character hole. Both.

**The second census hit, for completeness.** `app.py:939` `Static(self.repo, id="repo-name")` —
`self.repo` comes from `on_input_submitted` → `_normalize_repo` (`app.py:882-905`, verified by
reading it), so it is operator-typed, not file-derived: **LOW**. It is LOW rather than
informational because a repo string is realistically *pasted* from a client README or ticket, so it
is not fully operator-authored. The sibling `TabStrip` at `:936` already routes the same value
through `Text.assemble`; only `:939` is bare. Same one-line fix.

---

## The three items the brief asked for

### (1) HIGH-1 under the security lens — what a `link` target actually does, and whether the fix holds

**The fix holds. I fired it; I did not take `Text(...)` on trust.**

`p1_markup.py`, nine markup classes × three call forms through `default_cell_formatter`:

```
pre-fix   escape(t)        Text  spans=0  markup_interpreted=False
regressed plain(t) bare    Text  spans=2  markup_interpreted=True
                           styles=['red', 'link file:///C:/Users/OP/.ssh/id_rsa']
shipped   Text(plain(t))   Text  spans=0  markup_interpreted=False
```

Against the shipped form, across `[bold red on white]`, `[blink]`, `[conceal]`, an unknown tag,
`[@click=…]`, `[/]`, `[/bold]`, `[red]` unclosed, and 5,000 nested `[red]`:
**`leaks/raises under shipped form: 0`.**

End-to-end through the real `CoverageScreen` under Pilot (`p2_endtoend.py`), shipped tree:
`OSC-8 emitted: False`, `render raised: False`, `markup shown literally: True` — for both a link
payload and a `[/]` payload.

**`M-SEC-1` — I reverted the wrapper and re-ran the same end-to-end probe.** Both halves flipped:

```
title '[red]rojo[/red] y [link=file:///C:/Users/OP/.ssh/id_rsa]abrir[/link]'
  OSC-8 hyperlink emitted to terminal : True
  \x1b]8;id=8430646;file:///C:/Users/OP/.ssh/id_rsa\x1b\\\x1b[1;30;104mabrir\x1b[0m\x1b]8;;\x1b\\
title 'acta firmada[/]'
  *** APP RAISED *** rich.errors.MarkupError: closing tag '[/]' at position 12 has nothing to close
      textual/widgets/_data_table.py:1891 _on_idle -> :1433 _update_dimensions -> :2064 -> :221
```

**So: what can a `link` target DO here?**

- **It reaches the terminal.** Textual renders a Rich `link` style through `Strip.render` →
  `rich.style.Style.render`, whose last statement wraps the text in
  `\x1b]8;id=…;{link}\x1b\\ … \x1b]8;;\x1b\\`. **This is not a styling-only tag.** Verified over
  seven schemes: `file://`, `http://`, `https://`, a `\\UNC\share` path, `vscode://` and
  `javascript:` all emitted OSC-8 with the target intact. (`ms-msdt:/id PCWDiagnostic` did **not** —
  the space breaks Rich's tag parser, not a defence; percent-encoding restores it.)
- **What the emulator then does is the emulator's choice, and I could not test it from here.**
  That is precisely why it must be treated as actionable: the application has handed an
  attacker-chosen URI to a component whose behaviour it does not control and cannot audit. For a
  practice that opens client-supplied files, a ctrl-clickable `file://` into the operator's home,
  or an `http://` exfiltration beacon, is a realistic outcome.
- **Beyond `link`, one other tag has a non-styling effect**: `[conceal]` renders as `\x1b[8m`
  (verified: `\x1b[8mCONTRASENA\x1b[0m`), which hides text the operator is being shown. The rest
  (`[bold]`, `[blink]`, unknown tags) are cosmetic. The nesting bomb was harmless.
- **And one effect the code review did not name: `[/]` is a crash.** An unbalanced closing tag in a
  sidecar title raises `MarkupError` from inside `DataTable._on_idle`, which is **not** on a path
  the screen can guard. `escape` prevented it pre-fix, `plain` alone did not, and `Text(...)` does.
  This makes the shipped fix an availability fix as well as an integrity fix.

**Is this the only such sink?** No — see SEC-H2. A full census of `mapper/` for data-derived `str`
into a markup-parsing sink returns **two** live hits (`app.py:253`, `app.py:939`) plus the one this
diff closed. Everything else is clean and was spot-checked: every `Static.update` receives a `Text`,
every view renderer returns `Text`, and the two remaining `DataTable.add_row` string cells
(`app.py:292`, `app.py:655`) are `escape`d.

I re-derived `LLR-N06.2.5`'s own figures rather than trusting them (`p12_verify.py`, AST walk of
every `mapper/**/*.py`):

```
notify sites total = 31   non-literal first arg = 19
  of those, markup NOT disabled = 0      <- the markup half is green; my claim holds
  of those, not routed through plain() = 15   <- the coercion half, unchanged, carried
```

The markup half holds. The **coercion half is still 15 sites** — that is `LLR-N06.2.5`'s ratified
open work, unchanged by this diff and **not re-reported here as new**; I record the re-derivation
only because I assert the markup half in this report and would not assert it unmeasured. (The doc's
parked total of 30 is now 31; a site was added since `d877784`.)

**The systemic gap:** the batch ratified a **derived census** for the `notify` sink family
(`LLR-N06.2.5`: *"the verification shall obtain the set of such call sites by derivation from the
tracked product sources at run time"*) and built none for `Static` / `Label` / `DataTable.add_row`.
`tests/test_darkside_census.py` — the file this diff touches — is a **hue** census, not a sink
census. **Recommendation (detection > prevention):** extend the ratified AST-census shape to a third
threshold — *no `Static(...)`, `Label(...)`, `DataTable.add_row/add_column/update_cell` argument may
be a non-`Constant` expression that is not wrapped in `Text`/`Text.assemble`/`escape`*. That arm
would have caught both census hits and the S-E regression, and it is the only control here that
survives the next person who writes a new screen.

**With the cost stated honestly, because I prototyped it.** The naive form of that walk
(`p12_verify.py`) returns **23 hits**, of which `app.py:253` and `app.py:939` are the two real ones;
the other 21 are helpers that return a `Text` (`self._label(...)`, `self._render_table()`,
`darkside.step_meter(...)`, `inspector.py`'s eight `_label` calls). A pure expression-shape walk
cannot tell those apart, so the arm needs the **exact-stripped-line pin** that
`test_darkside_census.py::_sites` already uses — a reviewed allowlist that a new sink cannot join
silently. That is more work than one predicate, and it is the shape the batch already ratified.

### (2) Is `_ORIGIN_CHARS = 120` defensible?

**As a number for its own line: yes, and I would leave it. As a security control: it is not where
the security is.**

**The bound works on the fixture it was built for.** Re-fired the module's own
`scalar_amplified()` on the shipped tree (`p10_forge.py`):

```
file = 56,686 B   load = 0.076 s   records = 199   total = 61,275 chars   amp = 1.08x
max record = 309 chars
```

against the code review's pre-fix **19.9 MB / 348×**. A ~320× reduction. Two asserted numbers
spot-checked and holding: the docstring's "57 KB" (measured 56,686 B) and "0.081 SECONDS"
(measured 0.076 s).

**Where the threshold stops being a control, and where it stops being a bound:**

- **Floor ≈ 4 characters.** `AT-P02d` needs `documento duplicado: '1' <- 1` distinguishable from
  `'d1' <- 'd1'`; below `len(repr('d1')) == 4` the pin reddens and the coercion-collision signal
  the requirement exists for is gone. 120 clears that by 30×.
- **There is no ceiling at which it stops bounding the record** — but that is the wrong question,
  because **the record count is the free variable**, not the record length. Measured (`p7_bound.py`):

  ```
  payload=3 dups=  1,000   file=    27,074 B   records=  1,000   warn_chars=    36,998   amp=1.4x
  payload=3 dups= 20,000   file=   540,074 B   records= 20,000   warn_chars=   739,998   amp=1.4x
  payload=3 dups=100,000   file= 2,700,074 B   records=100,000   warn_chars= 3,699,998   amp=1.4x
  ```

  For **this** producer the count is file-linear, so the aggregate stays at ~1.4× and any value from
  roughly 8 to 2,000 is equally sound. **120 is a legibility choice, not a security parameter, and
  the justification "generous enough for any id an operator would recognise" is the honest one.**

**The defensibility problem is scope, not value.** `_ORIGIN_CHARS` bounds **1 of the 11
`load_warnings` producers in `store.py`** (`:68 :143 :149 :233 :246 :251 :457 :479 :491 :499 :516`).
The other ten interpolate `owner`/`nid`/`raw_nid` with no length bound at all, and one of them —
`:246`, added by this diff — is a **9,092×** amplifier, 26× worse than the 348× the bound was built
to stop. A per-record display threshold on one line is not a materialisation control for the module.
The control that would be is the sink cap in SEC-H1.

### (3) The truncated hostile scalar, into a toast

**The toast sink holds. Truncation created no payload in any of the 14 classes I drove.** This is
the item I expected to find something in and did not.

`p9_truncation.py` drives the exact shipped pipeline — `repr(value)[:120]` → `"; ".join` →
`darkside.plain` → the `markup=False` `notify` — over: a CSI sequence cut mid-escape, an OSC-52
clipboard write, `U+202E`, unclosed `U+2066` isolates, 300 `U+0301` combining marks, a `U+200D`
chain, a 300-code-point `U+E0020`–`U+E007F` TAG-block payload, an unterminated `[link=`, a
`[red]…[/red]` cut mid-tag, an astral run, 100 lone `U+D800` surrogates, a `bytes` payload with an
embedded escape, CRLF injection, and a record-separator payload.

- **No live control byte reaches the toast in any case.** The probe asserts on `ESC`, `BEL`, `CR`,
  `U+202E` and `U+200D` being present in the output string; **it never fired.** The reason is
  ordering that happens to be right: `repr()` runs **before** the slice, and Python's `repr` escapes
  every non-`isprintable()` code point — all of Cc, Cf, Zl, Zp, lone surrogates and the TAG block —
  into ASCII backslash sequences. `darkside.plain` then runs over a string that no longer contains
  them. The two guards are redundant here, which is the correct posture.
- **Truncation introduced no new code point.** Set difference between the truncated body and the
  full `repr`, over all 13 `str`/`bytes` cases: **empty**. Slicing a `repr` cannot forge an escape,
  because `\x1b` in a `repr` is four literal ASCII characters; cutting it yields `\x1`, not `ESC`.
- **A truncated markup tag is inert**: both toast sites pass `markup=False`, verified at
  `app.py:543/550/1289`.

**Two residuals, both LOW.**

- **SEC-L1 — combining marks are outside every guard.** `COERCION_RANGES` is exactly Cc/Cf/Zl/Zp;
  `Mn` is not in it, and `Mn` is `isprintable()` so `repr` passes it too. Fired: the 300-mark
  payload's truncated body **ends on `U+0301`**, which then stacks onto the `…` and, after the
  `"; "` join, onto the next record. Cosmetic/spoofing-adjacent, not a control-byte class. I do
  **not** recommend adding `Mn` to `COERCION_RANGES` — it would break legitimate Spanish and
  indigenous-language titles. If anything is done, normalise to NFC and cap consecutive marks.
- **SEC-L2 — record forgery in the joined toast.** Records are joined on `"; "` and no producer
  escapes `"; "` in a body. `store.py:499` (`campo ilegible: {nid}.fields`) interpolates the id with
  **no `repr` at all**. Fired (`p10_forge.py`), node id
  `x; nodo fantasma: 'raiz'; campo ilegible: todo_bien`:

  ```
  records actually emitted: 2
  toast the operator reads:
    nodo fantasma: "x; nodo fantasma: 'raiz'; campo ilegible: todo_bien"; campo ilegible: x; nodo fantasma: 'raiz'; campo ilegible: todo_bien.fields
  records the operator COUNTS by splitting on '; ': 6
  ```

  Two real diagnostics are read as six, one of them a fabricated `nodo fantasma: 'raiz'` naming a
  **healthy** node. It is a diagnostic-integrity defect, not an execution one, and the SEC-H1 sink
  helper is where a fix belongs (one record per line, or `repr` at every id interpolation).

---

## MEDIUM findings

### SEC-M1 — the HIGH-1 fix has no arm; the gate item is half-discharged

**Where:** `tests/test_repair_sidecar.py:364-389`.

The code review's clearing condition read: *"`Text(darkside.plain(...))` at `coverage.py:94`, **plus
an arm asserting `default_cell_formatter(cell).spans == []` for a markup-bearing title**."* The
first half landed. The second did not: the only coverage-screen arm is still the AST arm asserting
`escape` is *absent* — the arm that, by the code review's own measurement, passed straight through
the regression.

**Fired — `M-SEC-1` against the whole suite.**

```
baseline  46075a4         997 passed, 19 deselected, 3 xfailed in 261.32s
M-SEC-1   Text() removed  997 passed, 19 deselected, 3 xfailed in 257.20s   exit code 0
          anchor match count = 1 | restored sha256 374779563fbc3987… MATCH
```

**Identical. Not one arm moved.** The mutant emits an OSC-8 hyperlink to the terminal with an
attacker-chosen target and kills the app on a `[/]` in a title — both fired and shown above — and
the 997-arm suite cannot tell it from the fix. The guard that closes a terminal-escape hole and an
app crash has **no detector**, in a stage whose own evidence is that this exact guard was silently
removed once and nothing noticed.

**Smallest fix** — six lines, and it is behavioural where the existing arm is structural:

```python
def test_coverage_cell_does_not_parse_markup():
    """The title cell is a markup-PARSING sink; `plain` does not escape markup."""
    from textual.widgets._data_table import default_cell_formatter
    from rich.text import Text
    from mapper import darkside
    hostile = "[red]x[/red] [link=file:///C:/secreto]abrir[/link]"
    cell = Text(darkside.plain(hostile))          # exactly what coverage.py:113 builds
    assert default_cell_formatter(cell).spans == []
    assert default_cell_formatter(cell).plain == hostile
```

Add a second arm for the crash class, since it is a different failure mode:
`default_cell_formatter(Text(darkside.plain("acta[/]")))` must not raise.

### SEC-M2 — no census owns the markup-sink rule

**Where:** `tests/test_darkside_census.py` (touched by this diff) against `mapper/darkside.py:531`.

`plain`'s docstring makes a claim about the *whole codebase* — *"Safety from markup comes from never
handing a file-derived `str` to a markup-parsing sink"* — and nothing verifies it. The batch has the
right instrument already (`LLR-N06.2.5`'s run-time AST derivation for `notify`); it is pointed at
one sink family out of four. See the recommendation under item (1). Both SEC-H2 hits and the S-E
regression are inside this gap.

### SEC-M3 — a shipped test docstring pairs a pre-fix number with "Measured on the shipped tree"

**Where:** `tests/test_repair_sidecar.py:269`.

> *"Measured on the shipped tree -- benign 31 chars; 5 levels 522,311 chars in 0.025 s. Five levels
> is driven here precisely because it is RED by four orders of magnitude…"*

**Spot-check, using the module's own `amplified()` helper at `46075a4`:**

```
levels=0: total=31 chars in 25.1 ms     <- holds
levels=5: total=107 chars in 18.3 ms    <- the shipped tree; 522,311 is the PRE-FIX figure
levels=6: total=107 chars in 17.0 ms
   ['campo ilegible: document[0].name', 'campo ilegible: document[1].name',
    "documento duplicado: '' <- document[1].name"]
```

On the shipped tree the arm is **green at 107 against 2,000 — 19× under the bound, not red by four
orders of magnitude.** The sentence mixes one shipped measurement (31) and one pre-fix measurement
(522,311) under a single "Measured on the shipped tree", and the "RED by four orders" clause is true
only of the reintroduced defect, which the sentence does not say. This is the same class the batch
keeps cataloguing — a true number one line past where it is true — and it is in the record a future
reader inherits. **Fix:** *"Benign is 31 chars and five levels is 107 on the shipped tree; with the
defect reintroduced, five levels emitted 522,311 chars in 25 ms — red by 261×."*

---

## LOW findings

- **SEC-L1** — combining marks pass every guard (above). No change recommended.
- **SEC-L2** — record forgery in the `"; "` join (above).
- **SEC-L3** — `app.py:939` `Static(self.repo)`: operator-typed, not file-derived. Same one-line fix.
- **SEC-L4 — noted only because `B-30` touches this function.** `MapStore.load` /
  `save` build `self.workspace / f"{map_id}.mmd"` with no containment check, and `app.py:846`
  passes an operator-typed name. `store.load("../../x")` resolves outside the workspace. Every
  `map_id` I traced is either a `DataTable` row key from a workspace listing or operator-typed, so
  this is self-harm, not attacker-controlled — **pre-existing, out of this diff, not a gate item.**
  Flagged because the `B-30` message change draws a reader's eye to exactly this line. One guard:
  `if Path(map_id).name != map_id: raise MapStoreError(...)`.

---

## Coercion posture relative to `fdbdd62`

**Net: a real gain at the render sinks, a real loss at the diagnostic sink.**

| | Change | Direction |
|---|---|---|
| `coverage.py:113` | `escape(title)` → `Text(darkside.plain(title))` | **GAIN.** Keeps the markup guard (0/9 classes leak, fired) **and** adds Cc/Cf/Zl/Zp coercion, which `escape` never did. Also closes an app-crash class (`[/]`). |
| `coverage.py:114-116` | `escape(",".join(missing))` → `darkside.plain(...)` inside `Text.assemble` | **GAIN.** `escape` was inert inside `Text.assemble`; `plain` is real coercion. |
| `store.py:457-460` | raw `{d.get('name')!r}` / `{doc.name!r}` → `_raw_origin` | **GAIN.** 348× → 1.08× on the module's own fixture; max record 309 chars. |
| `store.py:547` | `Map not found: {mmd_path}` → `no existe el mapa {map_id!r}` | **GAIN.** The operator's home directory no longer reaches a toast or a screenshot. |
| `store.py:491` | new `nodo fantasma: {nid!r}` | **NEUTRAL-to-LOSS.** Correct per `LLR-REPAIR.1`; `nid` is unbounded but file-linear (one record per id). |
| **`store.py:246`** | **new `adjunto sin campos: {owner}.{key}[{i}]`** | **LOSS — SEC-H1.** 9,092×, 0.84 s, 2.0 GB. |

---

## To clear the gate

1. **SEC-H1** — cap `load_warnings` at the sink (`app.py:548`, `:1287`) and/or at the append, and add
   the `attachment_amplified()` fixture to the existing `< 2_000` oracle. Measured red at
   20,107,707 vs 2,000 — 10,053×, deterministic, 0.06 s.
2. **SEC-H2** — `darkside.plain` at `app.py:3342` **and** `Text(...)` at `app.py:253`. Both, not
   either. Add an arm that drives `[@click=screen.confirm]` through `_ConfirmScreen` and asserts the
   callback is not called on a click — the probe at `C:\Users\jjgh8\clde\secrev\p6_confirm_bypass.py`
   is the arm, ready to lift.
3. **SEC-M1** — the behavioural coverage-cell arm the code review already required.
4. SEC-M2, SEC-M3 and the LOWs are recommendations. SEC-M2 is the only one that changes the odds of
   a fourth instance of this class; SEC-M3 is a correction to the record and should land with the
   HIGHs.

SEC-H2 and SEC-L3/L4 are **outside `fdbdd62..46075a4`**. I am not blocking S-E for a defect S-E did
not introduce — **SEC-H1 alone is the block.** SEC-H2 is nevertheless a HIGH that this gate found
and that must be scheduled, not carried silently: it is live on `main`, it defeats a destructive
action's only human gate, and the batch has now written the fix pattern for it twice.

## Evidence checklist

- [x] Each finding has what · where · why · recommendation — SEC-H1, SEC-H2, SEC-M1…M3, SEC-L1…L4.
- [x] Each finding has a severity rating — 2 HIGH, 3 MEDIUM, 4 LOW.
- [x] No secret values in this output — hostile fixtures are synthetic; hostile code points named as
      `U+XXXX` per `C-56`; the one home-directory-shaped string is constructed, not read.
- [x] Verdict explicit — **BLOCK**.
- [x] New tool / integration scope and blast radius — no new dependency, MCP, connector or outbound
      surface in this diff. The *existing* blast radius is addressed: OSC-8 to the terminal emulator
      (item 1), Textual actions from file content (SEC-H2), and `load_warnings` → `notify` (SEC-H1).
- [x] Tree left byte-identical to `46075a4`, sha256-verified per file, `__pycache__` purged.
