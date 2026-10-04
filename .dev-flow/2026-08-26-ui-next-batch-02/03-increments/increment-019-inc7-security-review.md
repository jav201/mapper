# Security Review — Inc-7, `91fdbbd` (the damaged-map card, both load paths)

| | |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` (sealed) |
| Increment | `019` — INDEPENDENT security review of Inc-7 |
| Protocol | FULL, per ruling `D35`. I authored none of this diff. |
| Subject | `91fdbbd` — `mapper/darkside.py`, `mapper/app.py`, `tests/test_repair_cycles.py` |
| Mirror used | `…/scratchpad/mirror-inc7-sec` at `7c99df6` (mirror commit `8447a82`) |
| Repo | untouched except this file |

## 0 · Instrument integrity (stated before any finding)

- **Mirror, not repo.** Every probe ran with `cwd` = the mirror and `sys.path.insert(0, cwd)`, and
  **every probe asserted and printed `mapper.__file__`**. All four printed
  `…/scratchpad/mirror-inc7-sec/mapper/__init__.py`. The `_editable_impl_mapper.pth` trap did not fire.
- **Digests held.** Mirror tree digest (`git ls-files | sort | xargs sha256sum | sha256sum`)
  = `d16866d162896182c68bfd9ddccd87f139ef958d5b60bd4e665aa5b25663b4fe` **before and after** the whole
  run, including the full lane. `git status --porcelain` in the mirror: **empty**.
- **No source file was round-tripped.** I wrote zero files into the mirror; every probe lives in the
  scratchpad root. The CRLF / `rb`-`wb` trap has no surface here.
- **Scratch files are not named after stdlib modules** (`probe_inc7_names.py`,
  `probe_inc7_containment.py`, `probe_inc7_loadcount.py`, `probe_inc7_blast.py`, `probe_escape_sink*.py`).
- **Base validity.** The repo advanced to `f0974b6` (`docs:` only) during the review.
  `git diff --stat 7c99df6 HEAD -- mapper/app.py mapper/darkside.py tests/test_repair_cycles.py`
  is **empty** — my base is byte-identical to HEAD for all three reviewed files.
- **Disclosure duty.** My probes spawned **8 local processes** (6 × `python`, 1 × `pytest`, 1 × `ruff`).
  **Zero network calls.** Temporary `.mmd` fixtures were created only under the system temp directory.
- **C-56 honoured.** Every hostile code point in every probe is built with `chr(0x…)` and named, never pasted.

## 1 · Scope reviewed

`mapper/app.py` `HomeScreen.on_mount` (the `damaged` set, `load_or_notice`, the recents-loop card
branch), `mapper/darkside.py` (`DECLARED_VOCABULARY`, `DAMAGED_MAP_GLYPH`), `tests/test_repair_cycles.py`,
plus the reachable blast surface behind them (`mapper/store.py:583-682`, `mapper/mermaid.py:78-118`,
`textual.widgets._data_table.default_cell_formatter`, `rich.markup.escape`).

## 2 · The five lenses, answered by measurement

### L1 — one hostile map costs one card, never the screen · **VERIFIED**

Driven end to end against a real `MapperApp` over a workspace of **9** maps (1 cyclic/refusing,
2 healthy incl. the `sano_vacio` control, 6 hostile filenames):

```
A. on_mount survived a workspace of hostile names: True
   rows painted: 9 / expected 9   missing: []
B. containment: 'roto' present: True | healthy neighbours still painted: True
   roto cells : ['roto', ' ⊘ dañado ', '—', '—']
   sano cells : ['sano', ' concept ', '2', '0']
   vacio cells: ['sano_vacio', ' concept ', '0', '0']
E. full screen render after hostile names: OK
```

The failure is contained per map, and **no second map's card depends on the first's failure**: the
only cross-map state is `damaged`/`broken`, both keyed by name, both written only on the owning
map's own failure. `roto` and `sano_vacio` are now distinguishable in the **non-name** cells, which
is the defect `PRED-VIS` reproduces. See **F1** for the one structural reservation.

### L2 — is a hostile map FILENAME safe at `escape(map_name)` → `DataTable.add_row`? · **SPLIT**

**`escape` here is NOT a no-op — `DataTable` is a markup-PARSING sink.**
`textual/widgets/_data_table.py:184-224`, `default_cell_formatter`, does
`if isinstance(obj, str): … text = Text.from_markup(content, end="")`.
So `B-64`'s *"no-op at non-parsing sinks"* half **does not apply** to this call; the `escape` is
load-bearing and correct.

**`S-F3`'s crasher family does NOT reach this sink — refuted by measurement.**
`rich.markup.escape`'s regex `(\\*)(\[[a-z#/@][^[]*?])` is the **same** tag pattern as the parser's
`RE_TAGS`, so anything the parser recognises as a tag, `escape` escapes. Brute-forced over
**22,620** strings (alphabet of 12 incl. `[`, `]`, `/`, `\`, `@`, `#`, `(`, `)`, `.`; length ≤ 4)
through `default_cell_formatter` **plus a real `Console.print`** so render-time `Style.parse` also fires:

| input | format + render crashers |
|---|---|
| raw `str` | **34** |
| `escape(str)` | **0** |
| `escape(str)`, restricted to Windows-legal filename chars | **0** |

Confirmed live: `mapa[red.mmd` and `mapa[bold]x.mmd` both paint a row and the screen renders.

**But `escape` performs NO coercion, and the name cell calls nothing else — see F2.**

### L3 — `SEC-H2`'s family at the new cells · **CLEAN**

The new `kind_cell` carries **zero data-derived text in either branch**: the damaged branch is the
constant `f" {DAMAGED_MAP_GLYPH} dañado "`, the healthy branch the literal `"legacy"`/`"concept"`,
and both styles are constants from `darkside`. `Text.assemble` does not parse markup in the text
position (only `Style.parse` runs, on constants). `nodos`/`docs` are `"—"` or `str(len(...))`.
**Inc-7 adds no new data-derived string to any sink.** The only data-derived cell on the row is the
pre-existing name cell.

### L4 — does the error message leak? · **CLEAN, with one LOW residual**

Both toasts pass `darkside.plain(...)` **and** `markup=False` (`app.py:605-608`, `620-625`).
The upstream refusals are already scrubbed: `store.py:592` names the map id, not `{mmd_path}`
(`B-30`); `store.py:604` and `:680` interpolate `type(exc).__name__`, never `str(exc)` (`F2`/`F8`);
and `mermaid.py:103`'s `ParseError(f"…unsupported syntax: {raw!r}")` — which *does* carry a raw line
of the untrusted file — is **caught and re-wrapped** at `store.py:645-668` without its message, so
file content does not reach the toast by that path. Measured toast:
`'no se pudo cargar roto: el mapa tiene un ciclo: a→b→a'`. See **F3** for the residual.

### L5 — the glyph itself · **CLEAN**

```
glyph codepoint U+2298   len 1   cell_len 1   category Sm   east_asian_width N
in COERCION_RANGES: False        plain(glyph) unchanged: True
member of DECLARED_VOCABULARY glyph column: True    (20 single-style rows)
```

Not in a coerced range, one cell wide, not a combining/format/bidi point, and drawn from the
declaration rather than invented. **It cannot itself be a vector.**

## 3 · Findings

### F1 — the card branch swapped a self-evident guard for an unenforced two-place invariant `[Severity: MEDIUM]`

- **What:** the branch condition changed from `if graph is not None:` to `if map_name in damaged:`,
  and the `else:` arm now dereferences `graph` (`Graph | None`) **unguarded** — `graph.schema`,
  `graph.nodes`, `graph.documents`. Screen safety no longer rests on a local fact; it rests on the
  global invariant *"every path that `return None`s also did `damaged.add(name)`"*.
- **Where:** `mapper/app.py:741-745` (the `else:` arm); invariant maintained at `:602-604` and `:620`.
- **Why it matters:** I **audited the invariant and it holds today** — `return None` occurs only in the
  `except` block, `damaged.add` is coupled to `broken.append` under the same `if name not in broken`
  guard, and `grep -n "broken"` shows `broken` is written nowhere else (`591`, `602`, `603` only).
  So there is **no reachable crash at `7c99df6`/HEAD.** What I measured is the **blast radius if it
  is ever broken**: an exception raised in the recents-loop body, at exactly the position
  `graph.schema` occupies, **propagates out of `on_mount` and kills the app** — it is not contained:

  ```
  File "…/mapper/app.py", line 751, in on_mount
      table.add_row(
  AttributeError: 'NoneType' object has no attribute 'schema'
  ```

  That is the whole screen, which is precisely the cost `C-3` / `LLR-N13.1.5` exists to cap. And
  **nothing enforces the invariant**: `pyproject.toml` declares no `[tool.mypy]`, there is no
  `.github/workflows/`, and ruff does not do type inference — so a future edit adding a second
  `return None` to `load_or_notice` compiles, lints and ships.
- **Recommendation** (for `software-dev`; I do not apply fixes) — restore local evidence in one line:

  ```python
  if map_name in damaged or graph is None:
      ...                      # the damaged card
  else:
      kind = "legacy" if graph.schema else "concept"
  ```

  This is a strict widening: it changes no behaviour today (the sets coincide) and makes the
  unreachable case degrade to **one damaged card** instead of the app.
- **State:** `executed` (measured) · mitigation `planned`, not applied.

### F2 — the damaged card paints a map NAME that is escaped but **never coerced** `[Severity: HIGH — CARRIED, not introduced by this diff]`

- **What:** the name cell's only defence is `rich.markup.escape`, which neutralises *markup* and
  performs **no coercion whatsoever**. `darkside.plain` — the project's declared single coercion
  funnel, whose `COERCION_RANGES` is the tree's one source of truth — is **not** on this path. A map
  **filename is attacker-chosen** in the shared-map threat model.
- **Where:** `mapper/app.py:747` — `table.add_row(escape(map_name), …)`.
- **Why it matters — driven against the project's own derived set, not a hand-built model:**

  | measurement | count |
  |---|---|
  | code points in `darkside.COERCION_RANGES` | **235** |
  | …legal in a Windows filename (`< 0x20` and `/ \ : * ? " < > \|` excluded) | **205** |
  | …surviving `rich.markup.escape()` verbatim | **205** |
  | …reaching the painted `Text` of the name cell verbatim | **205** |
  | …that `darkside.plain` **would have** coerced to U+FFFD | **205** |
  | …of those, the U+E0020–U+E007F **TAG block** | **96** |
  | …bidi overrides/isolates (U+202A–U+202E, U+2066–U+2069) | **9** |

  Confirmed end to end through the real `HomeScreen`, with the files actually created on this
  filesystem and the code point surviving into `Path.stem`:

  ```
  tagblock  row painted=True  uncoerced: ['U+E0041']  plain() would coerce: ['U+E0041']
  rlo       row painted=True  uncoerced: ['U+202E']   plain() would coerce: ['U+202E']
  shy       row painted=True  uncoerced: ['U+00AD']   plain() would coerce: ['U+00AD']
  zwj       row painted=True  uncoerced: ['U+200D']   plain() would coerce: ['U+200D']
  ```

  The TAG block is the payload channel `darkside.py:488-491` singles out by name: *"those points
  render as nothing everywhere, map 1:1 onto ASCII, and reach an exported SVG as a payload the
  operator cannot see and any later reader recovers trivially."* U+202E lets a hostile `.mmd`
  **visually reverse its own name** in the sala.
- **Attribution, stated precisely — this diff neither introduces nor worsens it.** `escape(map_name)`
  is byte-identical in the pre-image; the pre-fix code painted the same cell 0 for a broken map
  (under the `concept, 0, 0` lie). Inc-7 changes cells 1–3 only. **Exposure is unchanged.**
- **But it is a SITE `B-64`'s driven sweep does not list.** That sweep's table
  (`increment-018-item3-pickups.md:57-62`) is organised by **sink mechanism** and covers three:
  `_clip → _CONTROL_MAP`, `darkside.plain`, and `escape → Text.append`. The mechanism here is a
  **fourth — `escape → default_cell_formatter → Text.from_markup`** — and the only `app.py` site
  driven end to end was `:511` (`_hero_text`). `B-64`'s census is already recorded as **stale**
  (pending item 1 of `018`) and its boundary as **closed in the bad direction** (pending item 2).
  This adds a fourth mechanism and a confirmed leak to that re-basing.
- **Recommendation:** the remedy is `B-64`'s post-merge body, not Inc-7's. What is owed **now** is
  cheap and is not a code change: **record this site and mechanism against `B-64`** so the re-basing
  acts on the real population. When the body lands, the fix is `escape(darkside.plain(map_name))` —
  `plain` first, then `escape`, because this sink parses markup and the two defences are orthogonal.
  Note the same argument applies to `escape(map_id)` / `escape(node_name)` at `app.py:713-716`, which
  are `Text.assemble` positions and therefore `B-64`'s *already-known* `escape → Text.append`
  mechanism; I did not re-drive them (out of scope).
- **State:** `executed` (measured) · remedy `blocked` — routed to `B-64`'s post-merge body, which the
  brief carries out of this increment's scope. Census amendment `planned`.

### F3 — the refusal toast carries attacker-controlled file content at unbounded length `[Severity: LOW]`

- **What:** `store.py:640-643` builds `f"el mapa tiene un ciclo: {CYCLE_ARROW.join(exc.cycle)}"` from
  **node ids read out of the untrusted `.mmd`**, and that string reaches the toast.
- **Where:** `mapper/store.py:641`, surfacing at `mapper/app.py:605-608`.
- **Why it matters:** no injection — `darkside.plain` coerces it and `markup=False` is passed, both
  verified. The residual is **footprint**: the cycle length and the id lengths are attacker-chosen,
  so the toast height is attacker-influenced. This is `N-C2`'s family (toast footprint, already a
  surfaced pending item), not a new class.
- **Recommendation:** cap the interpolated cycle (e.g. first 3 ids + `…`) when the post-merge toast
  work lands. Not owed by Inc-7.
- **State:** `executed` (measured) · mitigation `planned`.

### F4 — a refusing map is parsed twice per mount `[Severity: LOW]`

- **What:** `load_or_notice` memoizes the *notification* (`broken`) but not the *load*. The
  alphabetically-first `.mmd` is loaded once by the hero fallback and again by the recents loop.
- **Where:** `mapper/app.py:648-652` and `:721`.
- **Why it matters:** measured `store.load` call counts per `on_mount`: `{'roto': 2, 'sano': 1}`.
  A 2× amplification of parse cost for the one map an attacker can guarantee is first (a leading
  space or punctuation in the filename). The expensive refusals are already netted at
  `store.py:609-628` (`RecursionError`, big-int `ValueError`), so this is cost, not a crash.
  Pre-existing; unchanged by this diff.
- **Recommendation:** none owed. Note it if a workspace-size budget is ever written.
- **State:** `executed` (measured) · mitigation `n/a — pre-existing, no remedy owed here`.

### Not findings — checked and clean

- **Secrets:** no key, token, credential, `.env` or private-config value in any of the three files.
  The `token` hits are colour-token prose. **No secret value appears anywhere in this report.**
- **New dependency / integration / MCP / Composio / outbound action / destructive command:**
  **none** — `n/a — the diff adds no external surface, no dependency, no network call, no write path.`
- **`DECLARED_VOCABULARY` is data, not behaviour** — 20 constant `(glyph, label, style)` triples and a
  2-element `COMPOUND_ROWS_PENDING_A_PROJECTION_RULE`. No import, no I/O, no execution.

## 4 · The author's measurements — reproduced or refuted

| Claim | My result |
|---|---|
| default lane `1158 passed, 20 deselected, 3 xfailed` | **REPRODUCED exactly** — `1158 passed, 20 deselected, 3 xfailed in 364.98s` |
| ruff `27` at equal scope | **REPRODUCED** — `Found 27 errors.` |
| `INK on PANEL` = 17.18:1 vs `#D28`'s 4.5 floor | **not re-run** — `not-run`; contrast is `ux`'s instrument, not mine |
| battery, 4 sites (3 arms RED / 2 arms RED / 1 arm RED / control SURVIVED) | **not re-run** — `not-run`; accepted from the author's record, see §6 |
| `⊘` is `01b` `V22` | **partially verified** — membership in `DECLARED_VOCABULARY` is measured; the row's presence in `01b-ux-decisions.md` is `not-run` (Inc-8's set-equality) |

## 5 · Verdict

- [ ] ~~OK to ship~~
- [x] **`BLOCK-UNTIL: F2-census`**
- [ ] ~~Block~~

**What this means, stated so it cannot be misread.** Inc-7's own security behaviour is **sound**:
containment is verified under a hostile workspace, the new cells introduce no data-derived string
to any sink, both toasts are coerced and markup-disabled, and the glyph is inert. `F1` is MEDIUM and
does not block. The one HIGH I measured (`F2`) is **carried, not introduced** — this diff leaves the
exposure exactly as it found it — and its *remedy* is explicitly out of this increment's fence.

What is owed before this clears is therefore **not a code fix** but the one act that keeps the carry
honest: **`B-64`'s census must record the fourth sink mechanism (`escape → DataTable.add_row →
Text.from_markup`) and this confirmed leak at `app.py:747`, with the 205/235 measurement.** `B-64`'s
census is already on record as stale and its boundary as closed in the wrong direction; shipping
Inc-7 while a *newly measured* leak stays unrecorded would let the post-merge body act on a
population that is wrong again. Once that record exists, F2 converts from an open HIGH in this
review to a tracked item with its measurements attached, and this verdict becomes OK-to-ship with
F1 outstanding as a MEDIUM.

**This verdict authorises nothing by itself.** It is not a deploy approval, it does not advance any
gate, and it does not reach the operator's standing authorization — **a HIGH finding blocks
regardless** (`/dev-flow` §Batch-kickoff authorization). Routing `F2` to the post-merge body is the
**coordinator's** call, not mine; I have named the fact and attached its measurements.

## 6 · What I did NOT run — declared, not glossed

1. **The 4-site mutation battery.** Not reproduced. Re-firing it means mutating source in the mirror,
   which trades a hash-stable instrument for a re-verification of the author's own record. I chose
   digest stability and say so rather than implying coverage. → `not-run`.
2. **The `20` deselected tests** (`-m 'not slow and not network'`) and anything network-marked. → `not-run`.
3. **`01b-ux-decisions.md` set-equality.** I verified `DAMAGED_MAP_GLYPH ∈ DECLARED_VOCABULARY`; I did
   **not** verify `DECLARED_VOCABULARY` against the source document. That is Inc-8's assertion and it
   cannot be written until `A-103`/`A-104` settle the compound-row projection rule. → `n/a — Inc-8's`.
4. **The POSIX case.** U+001B (ESC) and the other 30 coercion points are illegal in a Windows
   filename but **legal on Linux/macOS**, where a filename can carry a raw OSC-52 clipboard write.
   `darkside.py:466-468` records that ANSI reaches the compositor verbatim (`S-B2`, measured). I
   **argued** this and did **not** measure it — no POSIX host. If mapper ships beyond Windows, `F2`'s
   severity rises from *invisible payload / bidi spoof* to *terminal control injection*. → `not-run`.
5. **Contrast (`#D28`)**, **the export budget**, and everything the brief carries out of scope
   (`FLAKE-1`, `.gitattributes`/autocrlf, `SEC-F4`, the socket guard, `B-64`'s post-merge body,
   `UX-HINT1`, `TC-F3-C`, `N3`, `S-F3`'s fix, the aesthetic glyph/tone choice). → `n/a — out of scope`.
6. **`app.py:713-716`** (`escape(map_id)` / `escape(node_name)` in the resume row) — the same family,
   `B-64`'s already-known mechanism, outside this diff. Named, not driven. → `not-run`.

## 7 · Evidence checklist

- [x] Each finding has what · where · why · recommendation — F1–F4 above.
- [x] Each finding has a severity rating — MEDIUM / HIGH (carried) / LOW / LOW.
- [x] No secret values appear in this output — secret scan over the three files returned only
      colour-token prose; hostile code points are named (`U+E0041`), never pasted.
- [x] Verdict is explicit — `BLOCK-UNTIL: F2-census`. The one HIGH is **present**, correctly
      attributed as carried, and it is **not** closed by a recommendation: the mitigation is
      `planned` / `blocked`, never `approved`, and the verdict reflects that.
- [x] New tool/integration scope and blast radius — `n/a — the diff adds none`; the blast radius
      that *was* measurable (a raise inside the recents loop) is measured in F1.
- [x] Instrument integrity — mirror named, `mapper.__file__` asserted in every probe, digest
      `d16866d1…` held across the run, no source round-trip, processes disclosed, no network.

---

## 8 · Addendum — the repo working tree MOVED under me, and I did not drive the delta

Recorded at hand-back, after my verdict was written. **None of it is mine** (my only repo write is
this file).

**What appeared.** At the start of my review `git status` in the repo was clean but for the
concurrent `code-reviewer`'s own report. At the end it carried **uncommitted modifications** to
`mapper/app.py`, `mapper/darkside.py` and `01-requirements.md` — a follow-up implementing the
concurrent review's findings: `DAMAGED_MAP_STATE` (the declared Spanish card string, replacing the
literal `dañado`), and the hero + resume surfaces gated on `damaged`.

**What that does to my verdict — read carefully.**

- **My review is of the COMMITTED state.** Every measurement in §0–§7 was taken in the mirror at
  `7c99df6`, which I verified byte-identical to `f0974b6` (HEAD) for all three reviewed files.
  **My verdict does not extend to the uncommitted delta.** → `not-run`.
- **I re-read the delta and my four findings survive it unchanged**, which I state because it would
  be dishonest to let the verdict quietly expire:
  - **F1 stands verbatim** — the recents-loop `else:` arm and its unguarded `graph.schema` are
    untouched.
  - **F2 stands verbatim** — `table.add_row(escape(map_name), …)` is untouched; the coercion gap
    is neither widened nor closed.
  - **L3 still holds** — `DAMAGED_MAP_STATE` is a module constant, so the kind cell still carries
    **zero** data-derived text.
  - **F3, F4** untouched.
- **One observation the delta adds, which REINFORCES F1.** The new resume block splits a binding
  from the guard that protects it, a second time:

  ```python
  if map_id and node_id:
      graph = load_or_notice(map_id)
  if map_id and node_id and map_id not in damaged:
      node = graph.nodes.get(node_id) if graph is not None else None
  ```

  `graph` is bound only inside the first `if`, and is relied on inside the second. It is safe today
  **only** because the two conditions share the `map_id and node_id` prefix, so the second cannot be
  true when the first was false — and because `graph` leaks in from the hero block above if it were.
  That is the **same shape as F1**: screen safety resting on a coincidence between two separated
  statements rather than on a local fact. F1's recommendation should be applied to both sites.
  This delta was not reviewed by me and I make no finding on it — it belongs to whoever gates it.

**A coordination hazard, flagged plainly.** The concurrent review numbered its findings `F1`/`F2`
in the **same increment `019`**, and those ids now appear in source comments (`app.py`: *"`F1`: THE
DECLARED CARD STATE"*, *"`F2`: THE ALL-ZERO SUBSTITUTION"*). **They are not my `F1`/`F2`.** Mine are
the unguarded `Graph | None` dereference and the uncoerced name cell. Two independent reviewers of
one increment minting colliding ids into permanent source comments is exactly the kind of drift
that makes a carry unreadable six increments later. The coordinator should re-key one set before
either report is cited.
