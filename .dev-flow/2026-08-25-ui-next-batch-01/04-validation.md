# 04 — Validation · `2026-08-25-ui-next-batch-01`

## BLUF

**All five P1 stories are validated through the shipped surface. The complete gate suite is
`205 passed`, exit code 0. Every acceptance test reconciles to exactly one on-disk node. One
verification is deliberately NOT a test and is recorded as such: the final hop to the operating
system (MAN-01).**

The batch found and fixed **five defects that existed before it started** and that the previous
suite could not see, because every one of them lives in the gap between "the action ran" and "the
key the operator presses reaches the action".

---

## 1 · The gate run (C-25 — orchestrator-owned, one complete run)

```
PYTHONUTF8=1 python -m pytest -q
205 passed in 21.32s
exit=0
```

Read from that run's own output, not stitched from partial runs. Baseline on `695bd2d` was
**88 passed**.

**Test ledger across the batch:** `205 = 88 − 6 + 123`. The six deletions are the four old keymap
tests and the two old palette tests, both superseded (see §4).

---

## 2 · Layer B — behavioural acceptance, black-box

Every `AT` drives the real mechanism. Where the story promises a keystroke, the test presses the
key; none substitutes a direct `action_*` call or a bare `.focus()` for the gesture it is
certifying. This is control **C-16**, and it is not ceremonial here: **the approving prototype is a
static SVG** (`prototypes/ui_next/generate.py` writes a cell buffer to `console.save_svg`), so it
contains no Textual widget, no focus model and no key handling. Every interaction claim in it was
unverified.

| Story | AT ids | Observed outcome |
|---|---|---|
| US-N01 edición in-situ | `AT-N01a` `AT-N01b` `AT-N01c` `AT-N01d` `AT-N01e` | a typed value survives a fresh `MapStore.load`; all four states persist; rows are labelled from `SchemaField.label`; a required-empty flag appears **and clears**; hostile sidecar text renders literally |
| US-N02 adjuntos | `AT-N02a` `AT-N02b` `AT-N02c` `AT-N02d` | add persists; the boundary is reached with the launcher injected; remove deletes exactly one and the survivors are pinned in order; a refused target is reported and never launched |
| US-N03 keymap único | `AT-N03a` `AT-N03b` `AT-N03c` `AT-N03d` `AT-N03e` `AT-N03f` | every seat entry resolves to an action its owner defines; a palette entry executes end to end; palette and help are scoped; the keybar names what it hides; bound keys equal the seat |
| US-N04 worklist | `AT-N04a` `AT-N04b` `AT-N04c` `AT-N04d` | `↵` jumps and focuses the first **missing** field; `n` walks the map and wraps; a complete map reports exhaustion; the empty report is a statement, not a fake row |
| US-N05 seguridad | `AT-N05a` `AT-N05b` `AT-N05c` `AT-N05d` | every archive is confirmed and a refusal leaves both text files byte-identical; accepting removes exactly that subtree; undo survives leaving and re-entering; an empty stack reports without raising |
| HLR-N06 focus | `AT-N06a` `AT-N06b` `AT-N06d` `AT-N06e` | the rail marks its selection only while it holds focus and the hint names the region; `escape` leaves a field keeping the value; regions collapse by key and by width |

### C-18 realization gate — executed, not asserted

```
total collected nodes : 205
distinct AT ids       : 27
AT ids with != 1 node : 0
C-18 VERDICT: PASS — every AT maps to exactly one on-disk node
```

The first run of this check **failed**: `AT-N03b` resolved to three functions, `AT-N04c` and
`AT-N06d` to two each. No acceptance was unrealized, so it was id hygiene rather than a coverage
gap — but an id naming several nodes cannot be traced. Fixed by splitting out `AT-N03f`, `AT-N04d`
and `AT-N06e` (commit `dd83725`), then re-run to the result above.

---

## 3 · Layer A — functional, white-box

Unit and integration coverage for the LLRs sits in `tests/test_keymap.py` (the seat's shape,
scoping, duplicate detection with a **positive control**), `tests/test_attachments.py` (the
`osopen` boundary: allowlist, confinement, type guard, no-shell, an AST-derived import ban),
`tests/test_inspector.py` (`Ficha.missing_required` ordering and whitespace handling),
`tests/test_rail.py` (subtree counts, collapse, keybar width) and `tests/test_coverage.py`.

### Counterfactuals — every load-bearing gate proven falsifiable

Eight mutations were executed, each reverted with its restore confirmed **by sha256**, and
`__pycache__` purged with the suite re-run green afterwards.

| # | Mutation | Reddened |
|---|---|---|
| M1 | delete `store.save` from the commit handler | `AT-N01a` + all four `AT-N01b` arms (5) |
| M2 | clamp the state setter to the default `"ok"` | 3 of 4 `AT-N01b` arms — **the `ok` arm stayed green** |
| M3 | remove `FieldInput`'s widget-level `escape` binding | `AT-N06b` alone |
| M4 | reduce the keybar marker to a bare `…` | `AT-N03e` alone |
| M5 | make the rail always paint the focused style | `AT-N06a` alone |
| M6 | restore the unconfirmed non-root archive | `AT-N05a` alone |
| M7 | move the undo stack back onto `MapScreen` | `AT-N05c` **and** `AT-N04a` (over-reported; see below) |
| M8 | focus `schema[0]` instead of the first missing field | `AT-N04a` alone |
| — | delete the workspace confinement check | 3 arms including the end-to-end `AT-N02d` |

**M2 is the measured argument for C-10.** Clamping the setter so it ignores its argument entirely
reddens three arms and leaves the default-valued one green. A single acceptance driven at the
default would have passed against a completely broken control.

**M7 over-reported, and that is recorded rather than rounded down.** It reddened `AT-N04a` as well
as its target, because the mutation shadowed the snapshot property and cascaded into the worklist
fixture. The target arm did redden, so the gate holds — but M7 is a coarser mutation than intended,
and `AT-N04a` does not independently guard undo placement.

**A failed counterfactual is also recorded.** The first attempt at M4 inserted unreachable code,
broke the parse, and produced **no test output at all**; the grep silently matched nothing. Had the
empty output gone unnoticed, a mutation that never ran would have been filed as evidence that the
gate holds.

---

## 4 · The superseded vacuous test

`tests/test_palette.py::test_palette_dispatches_selected_action` typed `"add"` into the palette.
No keymap entry matched — every label was Spanish prose — so the list was empty,
`action_run_selected` dismissed with `None`, and the final assertion
`not isinstance(app.screen, CommandPalette)` was **true precisely because nothing dispatched**. It
passed against a palette in which 0 of 33 entries worked.

Replaced by `AT-N03a`, whose input set is derived from `KEYMAP` at import time and fenced by exact
per-scope counts, plus `AT-N03b`, which drives `ctrl+p` → query → `enter` and asserts the
*observable effect* rather than the palette closing. The boundary case the old test accidentally
exercised is now asserted deliberately, as a negative, under its own name.

---

## 5 · Verification that is NOT a test — MAN-01

**The hop from `open_external(...)` to the operating system's default application has no honest
black-box oracle** short of launching a real program on the test machine. The `qa-reviewer`
declined to invent one, and that judgement was accepted.

- **Method:** `inspection`.
- **What is inspected:** `mapper/osopen.py`'s two launch paths — `os.startfile(target)` on Windows
  (single positional argument, no command line) and list-form `subprocess.run(["xdg-open", target])`
  elsewhere. Verified absent from the module: `shell=True`, `os.system`, any string interpolation
  into a command line.
- **What `AT-N02b` does and does not prove:** it gates the whole chain up to and including the call
  to the seam, with the launcher injected. **A green `AT-N02b` is not sign-off for MAN-01.** It is
  recorded here as covered-by-inspection, not counted as tested.

---

## 6 · Defects found by this batch that pre-dated it

Every one was invisible to the previous suite, and four of the five were found only because a test
pressed a real key.

| # | Defect | How it was found |
|---|---|---|
| 1 | `ctrl+p` never opened mapper's palette. `MapperApp` set `COMMAND_PALETTE_ENABLE`; Textual reads `ENABLE_COMMAND_PALETTE`, so the built-in palette owned the chord. | `AT` pressed the real key; the old test called `action_palette()` directly |
| 2 | `q` quit the application from the plug-repo and import-preview screens, discarding an unsaved import, while help advertised no such key. | independent code review |
| 3 | `escape` while typing in the search box popped the entire map and discarded the text. | UX lens, driven against the shipped app |
| 4 | `m cobertura` — the entry point to the coverage flow — was cut off the keybar entirely (216 cells rendered at a hard-coded 118). | UX lens measurement |
| 5 | `x` destroyed a non-root subtree with no confirmation, and the undo history died on leaving the map, making it unrecoverable. | the story itself; reproduced before fixing |

Plus two the security lens **executed** rather than argued: a `..` traversal target launched a file
outside the workspace, and `calc.exe` and `powershell.exe` both launched.

---

## 7 · Gate verdict

| Axis | Status |
|---|---|
| **Coverage** | ✓ Every US has its `AT` chain and every `AT` resolves to exactly one on-disk node; no orphan tests. |
| **Certainty** | ✓ Eight executed counterfactuals, per resolved arm, restores hash-verified. The one vacuous test in the tree was identified and replaced. Positive controls present where a refuse-everything implementation would otherwise pass. |
| **Evidence** | ✓ Every claim above cites a command output, a `file:line` or a collected node id. |

**One item is outstanding and it is a gate condition, not a nicety:** the independent
`security-reviewer` sign-off on Inc-4 was made a PDR condition and must return clean before merge.
Recorded as ⚠ pending here rather than assumed.
