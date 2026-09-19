# Security Review — Increment 018 · `SEC-H2` · independent re-measurement

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` (sealed) |
| Reviewer | `security-reviewer`, independent — authored none of this diff |
| Subject commit | `3ef067c` *fix(security): SEC-H2* on `feat/ui-next-batch-02` |
| Repo `HEAD` at start of review | `152ecd9` |
| Repo `HEAD` at end of review | `2c74347` — **the tree moved under me**, see `S-F1` |
| Date | 2026-09-19 |
| **Verdict** | **`SEC-H2` is CLOSED on my own measurement.** 0 HIGH open. 3 MEDIUM + 3 LOW recorded, none blocking. **This authorises nothing and is not a deploy approval.** |

> **No HIGH was cleared on the corrective pass's own report.** I reproduced the
> defect myself on the unfixed shape before accepting any closure, and every
> closure below rests on a measurement I took, with the instrument first shown
> able to report FAILURE. Where my measurement corrects the coordinator's brief,
> mine is stated and the brief's is named.

---

## Mirror, and hash-stability of what I measured

All probing, mutation and lane work ran **outside the repo**, in two sandboxes:

- **Mirror (read/measure):** `…\scratchpad\mirror-sec-h2`
- **Mutation sandbox (`mut2`, copied from the mirror):** `…\scratchpad\mut2`

| Item | Result |
|---|---|
| Default lane, mirror | `1143 passed, 20 deselected, 3 xfailed in 360.14s` — **reproduces the packet exactly** |
| Default lane, `mut2` (twice, under two probes) | `1143 passed / 20 deselected / 3 xfailed` both times |
| `mapper/app.py` digest, start **and** end | `19aece4e2d44daae` — held |
| `tests/test_confirm_markup.py` digest, start **and** end | `8897282bf74b030b` — held |
| `mut2` after the full mutation battery | **byte-identical restore**, both files |
| Arms content-identical to the repo's? | **yes** — normalised sha `d608ac51a82f4db7` equals the repo's file sha |
| Written by me in the repo | **this file only.** No tracked file moved by me. |

**Three defects in my own instrument, found and reported rather than hidden
(`S-F3`).** The brief's description of the mirror is wrong in three ways:

1. **The mirror is not the full tracked tree.** It tracks **282** files; `3ef067c`
   tracks **303**. The entire `prototypes/` tree (24 files, including
   `generate.py` / `prototype.py`) is present **on disk** but **absent from the
   mirror's git index**. Every `git ls-files`-driven gate — the `C-56` hostile
   code-point sweep, the `A3` census — therefore runs on a **weaker set** in the
   mirror than in the repo. I drove my own census from `rglob`, not `ls-files`,
   so it did cover `prototypes/`.
2. **The mirror is not `3ef067c`.** It contains three `.dev-flow` files that exist
   only at `HEAD` (`increment-017-qa-F3.md`, `increment-017-ux-F7-AT058.md`,
   `increment-018-item3-pickups.md`). It is `HEAD`-ish minus `prototypes/`.
3. **Line endings — I initially mis-read this and correct myself.** The brief's
   table (`test_confirm_markup.py`, `lane.py`, `export.py`, `state.py` = LF) is
   **correct for the repo working tree** — I verified it. It is **not** true of
   the mirror, which is **uniformly CRLF** (`git archive` normalised on the way
   out). So a multi-line anchor tuned to the brief's table matches 0× in the
   mirror, which is what happened to me once. The mirror is content-identical to
   the repo modulo line endings, not byte-identical.

---

## Scope reviewed

`git show 3ef067c` — 2 files, +198/−2: `mapper/app.py` (+32/−2),
`tests/test_confirm_markup.py` (new, 168 lines).

Blast radius read, not diffed: `mapper/darkside.py`, `mapper/store.py`,
`mapper/model.py`, `mapper/mermaid.py`, `mapper/widgets/inspector.py`,
`mapper/views/{layered,outline,radial,lane}.py`, `mapper/screens/*`,
`mapper/github.py`, `mapper/export.py`.

**Not run, and therefore not claimed:** the slow lane, the network lane, `ruff`,
and any lane inside the repo itself. **Carried, not in scope, not reviewed:**
`FLAKE-1`, `.gitattributes`/`autocrlf`, `SEC-F4`, the socket-level guard,
`B-64`'s post-merge body, `UX-F7b`, `UX-HINT1`, the export budget.

---

## Disclosure

One probe of mine (`RepoScreen` with a markup payload as the repo identifier)
drove `GitHubConnector`, which **spawned the `gh` CLI and made a real outbound
GraphQL call to GitHub** under the operator's credentials. It was a read-only
repository lookup that failed (`GraphQL: Could not resolve to a Repository`).
**A stray audit-log line at GitHub dated 2026-09-19 for a nonsense repository
name is mine.** No secret was transmitted or printed.

---

## The defect, reproduced by me before any closure

The original probe was gone, so I rebuilt it. On the **vulnerable shape**
(`Static(str)` with markup at its default `True`), payload
`[@click=screen.confirm]Acta[/]` inside `archivar «…»?`:

| Shape | Painted row | Segment style meta |
|---|---|---|
| `markup=True` (unfixed) | `archivar Acta?` — **identical to the benign sentence** | `{'@click': 'screen.confirm', 'offset': (9, 0)}` |
| `markup=False` (the fix) | `archivar [@click=screen.confirm]Acta[/]?` | `{'offset': (0, 0)}` — **no action bound** |

This is stronger evidence than the packet's, which read only the painted string.
I read the **segment style meta**, which is the property the finding is actually
about: the unfixed sink really does bind a runnable action to the words the
operator reads, and the fixed sink really does leave zero bound actions — not
merely zero visible tags. The finding was real and the fix addresses the
mechanism, not the symptom.

### The three fired impacts, each measured end-to-end

Driven through the real app (`MapperApp` → `MapScreen` → ficha modal → `x`
chord), payloads built with `chr(0x5B)` per `C-56`:

| Impact | Payload | Result on the shipped tree |
|---|---|---|
| (a) action binding | `[@click=screen.confirm]Acta[/]` | **CLOSED** — painted literally, no action |
| (b) concealment | `[conceal]oculto[/]` | **CLOSED** — painted literally |
| (c) uncatchable crash | `[@click=screen.confirm?` and `[/` | **CLOSED on this path** — app survives |

**Correction to the finding's own wording on impact (c).** An *unclosed* tag does
**not** kill the app on Textual 8.2.8 — `[bold]never closed` renders fine. What
kills is a **malformed value tag** (`[@click=screen.confirm?`, `[/`), which
raises `MarkupError` out of the compositor. The distinction matters because it
changes what a regression arm must use as a payload.

---

## Item 1 — Is the sink fix COMPLETE? **Yes, verified.**

- **`_ConfirmScreen` has exactly one production caller**, as claimed:
  `mapper/app.py:3868` (`push_screen(_ConfirmScreen(message), callback=do_archive)`).
  Derived by tree-wide grep; the only other references are the class definition,
  a CSS selector, and two test files.
- **`#confirm-hints` cannot take untrusted text.** It is constructed as
  `Static("", id="confirm-hints")` and updated once, at `mapper/app.py:311`, with
  `Text.assemble(…)` over **four constant strings**. A Rich `Text` is routed to
  `Content.from_rich_text`, never `Content.from_markup` — the grammar cannot run
  on it regardless of the widget's markup flag.
- **No other widget in that modal takes data.** The modal is exactly
  `Vertical(Static(message, markup=False), Static("", id="confirm-hints"))`.

---

## Item 2 — Census of markup-parsing sinks fed by untrusted data

**This is the item of most value, and it changes the shape of the answer.**

### How the set was derived (not hand-built)

1. **Sink names derived from the installed library**, not from my head: walked
   every `textual.*` module and collected every class/function whose signature
   carries a `markup` parameter — **43 callables**. That over-collects (`markup`
   is inherited from `Widget.__init__`, so containers appear), so:
2. **The true parse condition was read out of Textual's source.**
   `textual.visual.visualize` runs the grammar **iff the object is a `str` and
   markup is enabled** — `Content.from_markup(obj) if markup else Content(obj)`.
   A Rich `Text` goes to `from_rich_text`; anything else is wrapped. So the sink
   condition is precisely **non-empty `str` + markup on**.
3. **A runtime probe drove the set from execution**, patching `Static.__init__`,
   `Static.update`, `App.notify` and `DataTable.add_row` to record
   *(call site, `type(content)`, markup flag)*, then running the **full
   1143-test suite**.

**Instrument shown RED before any PASS was believed:** the probe was first run
against a fixture with four known cases and correctly discriminated all four —
`str`+markup → recorded dangerous; `str`+`markup=False` → safe; Rich `Text` →
safe; `.update(str)` → caught.

> **Two earlier versions of my probe were wrong and I discarded them.** Patching
> `Content.from_markup` attributes every hit to `asyncio`, because `Static`
> *stores* content at `__init__` and visualises it later inside the render pump —
> the constructing frame is gone by parse time. Reported as `S-F3`; it is the
> reason a chokepoint census cannot answer this question.

### Result — 91 sink sites exercised

Every markup-**enabled** site that received a **non-empty `str`**:

| Site | Value observed | Trust |
|---|---|---|
| `app.py:240` `Static(self.title)` — `_PromptScreen` | `'ruta o url del adjunto'` | **constant** (all 7 callers literal) |
| `app.py:700` `DataTable.add_row` | `'anidado'`, `'7'`, `'0'` | map name (file-derived) — see below |
| `app.py:921` `Label(…)` | `'conectar repositorio'` | constant |
| `app.py:985` `Static(self.repo)` | `'jav201/taskboard'` | operator-typed, shape-validated |
| `app.py:988`, `app.py:3766` | hint / status text | constant |
| `coverage.py:70`, `settings.py:37`, `settings.py:66` | `'cobertura incompleta'`, `'switch'`, … | constant / internal |
| `help.py:72` | `'atajos · map'` | internal scope name |

**Everything else was the empty string** (placeholder `Static("")` widgets later
updated with Rich `Text`).

**`mapper/app.py:299` is the only `Static` in the entire application observed
with markup DISABLED**, and the probe captured it receiving the hostile values:
`'¿archivar «[@click=screen.confirm]Acta[/]»?'` and `'¿archivar «acta��firmada»?'`
(two `U+FFFD`). **Both halves of the fix are confirmed live at runtime, across
the whole suite, by an instrument that did not know what it was looking for.**

### The two file-derived candidates, resolved

- **`app.py:700-701` `table.add_row(escape(map_name), …)`** — `map_name` is a
  `.mmd` filename stem. `DataTable` uses **Rich's** parser, which is *permissive*:
  it accepts `[-=!`, `[@=#`, `[/`, `[@click=x?` where Textual's `Content`
  rejects all four. Measured end-to-end: every payload renders **literally**,
  including a well-formed `[@click=…]`, because `escape` handles well-formed
  tags. **Not a hazard.**
- **`app.py:985` `Static(self.repo)`** — markup is on and the value is typed by
  the operator, but `GitHubConnector` rejects anything that is not `owner/name`
  **before** the value is used. Measured: **zero `MarkupError`** across four
  payloads. **Not a hazard.**

### Conclusion

**No live markup-parsing sink in `mapper/` is fed by untrusted, file-derived
data.** The census owed by the original finding is discharged, and it comes back
clean apart from the latent twin recorded as `S-F2`.

The wider control-character surface the census also surfaced (the `_FichaScreen`
modal at `app.py:373-427` and several `factory.py` sites use `escape` only, with
no `darkside.plain`) is **`SEC-F4` territory — carried, not in scope here.** Those
sinks build Rich `Text`, so no grammar executes on them; the exposure is faithful
control characters, not runnable actions. **I am not closing `SEC-F4`.**

---

## Item 4 — Is `darkside.plain` the right coercion, and is the source site unique?

**Yes, and yes — with one boundary worth stating.**

`darkside.plain` maps 235 code points — Unicode `Cc`+`Cf`+`Zl`+`Zp` minus TAB/LF —
each to a single `U+FFFD`. That covers both code points the finding named
(`U+202E`, `U+200D`) and the rest of the bidi and zero-width families.

It deliberately does **not** touch `[` or `]`. That is correct: markup safety
here comes from the **sink** (`markup=False`), not from the source. The two
halves are genuinely different hazards, exactly as the packet claims — I verified
this by mutation (below), where reverting either half left the other arm green.

`name = darkside.plain(node.ficha.title or node.id)` (`app.py:3846` at `3ef067c`,
`3901` at `HEAD`) is the **only** site that builds the confirmation's quoted
name; the archive toast eight lines above independently coerces the same value.

**Boundary, stated not hidden:** `plain` does not bound **length**, does not strip
**combining marks**, and does not neutralise **strong-RTL script characters**
(as opposed to bidi *control* characters). A title written in Hebrew or Arabic
letters still reorders a line under the Unicode bidi algorithm. That is inherent
to displaying text, not a defect in `plain`, but it means "the operator sees the
words in the order they were written" is guaranteed against *control characters*
only.

---

## Item 5 — Attacking the oracle

`_painted()` reads `widget.render_line(y)` and joins segment text. I attacked it
three ways.

1. **Is reading the painted frame sound?** Yes, and it is the right choice: both
   states hold a `Content`, so stored content cannot distinguish them. I
   independently corroborated the oracle against a **different** observable —
   segment style meta — and the two agree (tags literal ⟺ no `@click` bound).
2. **Can it silently return nothing?** Its `except Exception: break` is broad, but
   **arms 1 and 2 each carry a positive control** (`"archivar" in painted`,
   `"acta" in shown and "firmada" in shown`). I sabotaged `_painted` to return
   `""` unconditionally: **both arms FAILED**, loudly. The oracle is guarded.
3. **The RED-proof arm does not prove what it claims** — recorded as `S-F4`.

### Mutation battery, re-run by me — reproduces the packet exactly

| Mutation | markup arm | coercion arm | arm 3 |
|---|---|---|---|
| baseline | PASS | PASS | PASS |
| **M1** sink reverted (`markup=False` removed) | **FAIL** | PASS | PASS |
| **M2** source reverted (`darkside.plain` removed) | PASS | **FAIL** | PASS |
| **M3** comment-only control | PASS | PASS | PASS |
| **M4** `_painted` sabotaged (mine) | **FAIL** | **FAIL** | **PASS** |

Restore after every mutation: **byte-identical** (`19aece4e2d44daae`).
Each half kills exactly its own arm — neither arm is carrying both, as claimed.

---

## Findings

### `S-F1` — The sealed repo moved during an independent review  [Severity: MEDIUM]
- **What:** `HEAD` went `152ecd9` → `2c74347` and `mapper/app.py` changed digest
  (`19aece4e2d44daae` → `3335d63a0ac43610`) while this review was running.
- **Where:** repo root; commits `344db11`, `63673ee`, `2c74347`.
- **Why it matters:** a reviewer's verdict names a tree. If the tree moves, the
  verdict silently stops describing the artifact. The 016 review reported a
  weaker form of this (files appearing during the read); this time the **reviewed
  source file itself** changed. A "sealed" batch that accepts writes is not sealed.
- **Recommendation:** either freeze the branch for the duration of a review, or
  require every review to state the digest it measured and re-assert it at the
  end — which is what saved this one.
- **Impact on this verdict: none, and I verified that rather than assuming it.**
  The `3ef067c..HEAD` change to `app.py` is the **export budget** (`A-100.4/.5`,
  carried out of scope), touching only hunks at `~3517` and `~3601`. I extracted
  both SEC-H2 regions from both revisions and compared them normalised:
  `_ConfirmScreen` **identical** (`87da1c4b2ce5291a`), archive-action block
  **identical** (`f760f3a6755ab658`), each fix line present exactly once at `HEAD`.
- **State:** `executed` (measured).

### `S-F2` — `_PromptScreen` is the unfixed structural twin of the fixed sink  [Severity: MEDIUM]
- **What:** `Static(self.title, id="prompt-label")` at `mapper/app.py:240` is the
  same shape the fix was applied to — a bare `str` into a markup-enabled `Static`
  — and it did **not** receive `markup=False`.
- **Where:** `mapper/app.py:240` (and its sibling `Static("", id="prompt-hints")`).
- **Why it matters:** **not exploitable today** — I derived all seven callers
  (`app.py:800, 825, 898, 2897, 3796`; `screens/factory.py:447`) and every title is
  a **literal constant**, which the runtime census confirms (`'ruta o url del
  adjunto'`). But the packet's own stated rationale for fixing at the sink was
  that *"the next message built there would inherit the hazard."* That reasoning
  applies verbatim to `_PromptScreen`, which is one f-string — e.g. a
  `"renombrar «{title}»"` prompt — away from being the same HIGH. The class fix
  was applied to one instance of the class.
- **Recommendation:** `Static(self.title, id="prompt-label", markup=False)`. One
  token, same idiom, closes the twin. Let `software-dev` apply it.
- **State:** `planned` — **not a blocker**, because no untrusted value reaches it
  on the shipped tree and I measured that.

### `S-F3` — `rich.markup.escape` does not neutralise malformed tags for Textual's parser  [Severity: MEDIUM]
- **What:** Rich's escape regex is `((\\*)\[([a-z#/@][^[]*?)])` — it requires a
  **closing `]`**. A malformed tag has none, so it passes through unescaped.
  Textual's `Content.from_markup` then raises `MarkupError`.
- **Where:** `from rich.markup import escape` in `mapper/app.py:10`,
  `darkside.py:40`, `screens/editor.py:6`, `screens/factory.py:7`,
  `views/lane.py:6`, `views/layered.py:7`.
- **Measured:**

  | payload | Rich `Text.from_markup` | Textual `Content.from_markup` |
  |---|---|---|
  | `[-=!` / `[@=#` / `[/` / `[@click=x?` | **OK** (all four) | **`MarkupError`** (all four) |

  An exhaustive fuzz over Windows-legal filename characters found **77 crashing
  payloads of length ≤ 4** against Textual's parser after escaping.
- **Why it matters:** `escape()` reads as a sanitiser and is not one *relative to
  a Textual sink*. Today **nothing exploits this** — every `escape()`ed value in
  `mapper/` lands in a Rich `Text` or in `DataTable` (Rich's permissive parser),
  both measured safe. It is a trap for the next `Static(escape(untrusted))`,
  which would be a crash surface on day one.
- **Recommendation:** treat `markup=False` as the only sink-correct control for
  Textual sinks, and note in `darkside.py` that `escape` is Rich-relative. This
  is the generalisable form of the packet's own maxim — *a coercion idiom is
  correct only relative to its sink*.
- **State:** `executed` (measured); mitigation `planned`.

### `S-F4` — The arm that claims to be the instrument's RED-proof does not exercise the oracle  [Severity: LOW]
- **What:** `test_sec_h2_the_oracle_can_tell_the_two_forms_apart`
  (`tests/test_confirm_markup.py:160-168`) is documented as *"Instrument RED-proof:
  the oracle must distinguish parsed from literal… without this, both assertions
  above could be true of an oracle that never looks at markup at all."* It never
  calls `_painted`. It asserts `"[@click=…]" in Text(f"x{PAYLOAD}y").plain`, which
  is Rich `Text.plain` echoing a literal — exercising neither Textual's grammar
  nor `render_line`.
- **Where:** `tests/test_confirm_markup.py:160-168`.
- **Why it matters:** proven vacuous **as an oracle proof** by mutation M4 —
  with `_painted` returning `""` unconditionally, arms 1 and 2 fail and **this arm
  still passes**. The real protection comes from the positive controls inside
  arms 1 and 2, not from this arm. The docstring therefore credits the suite with
  a guarantee the suite does not hold, which is the precise failure mode this
  batch's control catalog exists to catch.
- **Recommendation:** make it assert on `_painted` itself — build one
  `Static(payload)` and one `Static(payload, markup=False)`, and assert
  `_painted` returns **different** strings for them. That is a genuine RED-proof
  and it fails if the oracle stops looking at markup.
- **State:** `planned`. Non-blocking: the arms it accompanies are sensitive, proven.

### `S-F5` — `prototypes/` is tracked, contrary to `.gitignore` and decision `D13`  [Severity: LOW]
- **What:** `.gitignore` lists `prototypes/` with the comment *"Throwaway UI
  prototypes… NEVER committed: … decision D13's ruff metric of 29 is only valid
  while they stay untracked — a bare `ruff check .` reads 57, and the other 28
  are all here."* The repo nevertheless tracks **24** files under `prototypes/`
  (`git ls-files prototypes | wc -l` = 24).
- **Where:** repo index; `.gitignore` final stanza.
- **Why it matters:** a documented invariant that a decision's metric depends on
  is violated, and the ignore rule masks it (a fresh `git add -A` will not
  re-add them, so the state is invisible to ordinary workflow). It also silently
  widens the `git ls-files`-driven gates (`C-56` sweep, `A3` census) relative to
  what their authors scoped.
- **Recommendation:** a coordinator ruling — either `git rm --cached prototypes/`
  and restate the ruff metric, or delete the `.gitignore` stanza and re-baseline
  `D13`. Do not leave the file and the index disagreeing.
- **State:** `executed` (measured); resolution `blocked` on a ruling.

### `S-F6` — My own mirror was materially incomplete  [Severity: LOW]
- **What / where / why / recommendation:** see *Mirror* above — 282 tracked vs
  303; `prototypes/` absent from the index; three `HEAD`-only files present;
  uniformly CRLF. A census driven from `git ls-files` in this mirror would have
  silently skipped 24 tracked Python-bearing files.
- **Mitigation applied:** I drove my census from `rglob` and re-`git init`-ed the
  mutation sandbox so the `ls-files`-dependent arms (`tests/test_views_hits.py`)
  could run; the full lane passed 1143 in that sandbox.
- **State:** `executed`; mitigation `executed`.

---

## Verdict

- [x] **OK to ship, from the security lens — `SEC-H2` CLOSED, 0 HIGH open.**
- [ ] `BLOCK-UNTIL:` — n/a, no HIGH open.
- [ ] Block — n/a.

`SEC-H2` is **CLOSED on my own measurement**, on the mirror named above, at
subject commit `3ef067c`, and — verified separately — the two fixed regions are
byte-identical at current `HEAD` `2c74347`. The closure rests on:
the defect reproduced by me on the vulnerable shape with the action-binding
**observed in segment meta**; the fix verified to leave **zero bound actions**;
all three fired impacts measured closed end-to-end through the real app; a
**derived runtime census over the full suite** showing `app.py:299` is the only
markup-disabled `Static` in the application and that **no live markup-parsing
sink is fed by untrusted file-derived data**; and a mutation battery in which
each half kills exactly its own arm.

**Every digest held.** `app.py` `19aece4e2d44daae` and
`test_confirm_markup.py` `8897282bf74b030b` were identical at the start and the
end of my run; every mutation restored byte-identically.

**What I did NOT run, and therefore do not vouch for:** the slow lane, the
network lane, `ruff`, and any lane inside the repo itself. My census is bounded
by what the 1143-test suite executes — a screen no test composes contributes no
runtime evidence, and for those I relied on the AST scan, which is weaker. I did
not review the carried items (`FLAKE-1`, `.gitattributes`/`autocrlf`, `SEC-F4`,
the socket-level guard, `B-64`, `UX-F7b`, `UX-HINT1`, the export budget), and
**`SEC-F4` in particular remains open** — the control-character surface in
`_FichaScreen` and `factory.py` is real, and nothing here closes it.

**This verdict authorises nothing.** It is not a deploy approval, and it is not
the operator's authorization; clearing a risk is not granting a release.

---

## Evidence checklist

- [x] Each finding has what · where · why · recommendation — `S-F1`…`S-F6`.
- [x] Each finding has a severity rating — 3 MEDIUM, 3 LOW, 0 HIGH.
- [x] No secret values appear in this output. Hostile code points are **named**
      (`U+202E`, `U+200D`), never pasted, per `C-56`; markup payloads are
      structural, not secrets, and were built with `chr(0x5B)` in my probes.
- [x] Verdict explicit, and **every HIGH ABSENT** — `SEC-H2` carries
      applied-and-verified evidence measured by me, not by the corrective pass.
- [x] New tool/integration scope — **none added** by this diff. Disclosed
      instead: my own probe spawned `gh` and made one outbound GitHub API call.

## Evidence states

| Item | State |
|---|---|
| `SEC-H2` defect reproduced on the vulnerable shape | `executed` |
| `SEC-H2` sink fix (`markup=False`) verified | `executed` · `approved` |
| `SEC-H2` source fix (`darkside.plain`) verified | `executed` · `approved` |
| Impacts (a)/(b)/(c) closed end-to-end | `executed` |
| Derived runtime sink census (full suite) | `executed` |
| Mutation battery incl. oracle sabotage | `executed` |
| Default lane reproduced (mirror + `mut2`) | `executed` |
| Slow lane · network lane · `ruff` | `not-run` |
| `S-F2` twin sink mitigation | `planned` |
| `S-F3` escape-vs-Textual mitigation | `planned` |
| `S-F4` RED-proof arm repair | `planned` |
| `S-F5` `prototypes/` tracking | `blocked` (needs a ruling) |
| `SEC-F4`, `FLAKE-1`, autocrlf, export budget, `B-64`, `UX-F7b`, `UX-HINT1` | `n/a — carried, out of scope` |
