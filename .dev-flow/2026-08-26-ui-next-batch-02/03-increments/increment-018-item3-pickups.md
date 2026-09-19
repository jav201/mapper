# Increment 018 — Inc-CONFIRM item 3 · the routed pickups

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Increment | `018` — Inc-CONFIRM item 3: `SEC-H2`, the `B-64` driven sweep, `F3`→qa, `F7`+`UI-AT058`→ux |
| Agent | `software-dev`, with `qa-reviewer` and `ux-reviewer` on their own mirrors |
| Date | 2026-09-19 |
| Commits | `3ef067c` (`SEC-H2`) + this docs commit |

---

## 1 · What changed

**One HIGH closed in code; three pickups returned as judgements; one carry's census found
stale.** `SEC-H2` is the only source change — the rest of item 3 is measurement and routing.

### `SEC-H2` — CLOSED (was a live HIGH)

**Confirmed live on this tree before being fixed, not taken from the S-E report.** The original
probe was gone, so the arms were written first and captured RED on the real defect. With
`[@click=screen.confirm]Acta[/]` as a node title, the archive confirmation **painted**
`¿archivar «Acta»?` — a sentence identical to the benign one, with a runnable action bound to
the words the operator reads. One click archives the subtree with no `y`. Separately, `U+202E`
and `U+200D` reached the dialog raw.

Two hazards, two fixes, and **they are not the same hazard**: `markup=False` at the **sink**
stops the title *acting* on the dialog; `darkside.plain` at the **source** stops it *reordering*
the sentence. Each is pinned by its own arm, and the battery mutates each half separately so
neither arm can be carrying both.

**Two of this tree's own controls caught this work, and both were obeyed rather than worked
around**: the A3 census refused the new arm while it was untracked (*"stage it, or the gate is
not a gate"*), and the `C-56` sweep refused the `\u202e` escape spellings, which are now built
with `chr(0x…)` at test time like every other hostile payload in the suite.

### `B-64` — the DRIVEN reachable-sink sweep, and the census it rests on is STALE

**The recorded census does not describe this tree.** The carry records *"38 sites: app.py 14,
factory.py 12, lane.py 7, editor.py 4, darkside.py 1"*. Derived by AST at `046acea`: **45 calls**
— app.py 17, factory.py 13, lane.py 9, editor.py 4, darkside.py 1, **and `views/layered.py` 1,
a file the census does not name at all**. Rider 2 says the carry travels with its measurements;
the population those measurements were taken over has moved.

Instrument validated before the count was believed: `app.py:319` genuinely holds **two** `escape`
calls on one line (so a line-count and a call-count legitimately differ); grep's extra
`darkside.py` hit is **prose describing the defect**, which is catalog entry 32 exactly (*an arm
that greps source lines counts descriptions of the defect as the defect*); and `office.py`'s six
`escape(` hits are `saxutils.escape` and `re.escape`, correctly excluded — so the AST neither
over- nor under-counts.

**The axis is the SINK MECHANISM, not the file.** A painted value is coerced iff it funnels
through a coercing truncator. Driven, through the real renderers:

| Site | Mechanism | Raw survivors | U+FFFD |
|---|---|---|---|
| `views/layered.py:679` (`eliminados` ghost) | `_clip` → `_CONTROL_MAP` | **none** | yes |
| `views/layered.py` (live card title) | `_clip` → `_CONTROL_MAP` | **none** | yes |
| `views/outline.py` (control) | `darkside.plain` | **none** | yes |
| `views/lane.py:156` (`LaneRenderer`) | `escape` → `Text.append` | **U+202E, U+200D** | no |
| **`app.py:511` (`_hero_text`)** | `escape` → `Text.append` | **U+202E, U+200D** | no |

**The carry's BOUNDARY is closed, in the bad direction.** It read *"Only `lane.py`'s three
renderers were driven end to end. The other four files were not."* `app.py:511` is the first
site outside `lane.py` driven end to end, and it **leaks**. The defect is not confined to
`lane.py`.

**And one genuinely good result:** `layered.py:679` — the only `escape` site in the **export**
path, feeding the `eliminados` strip whose titles come from a previous revision — **does not
leak**. `layered._clip` documents itself as the single coercion funnel for that module
(*"LLR-COERCE.2: coerce, THEN truncate … EVERY truncator in this module funnels through here"*)
and the measurement agrees. That `escape` call is a redundant no-op, not a hole.

`U+0007` survived nothing, consistent with the carry's own note that the loss is
**bidi-and-joiner, not every control byte**.

---

## 2 · Files modified

| File | Kind | Change |
|---|---|---|
| `mapper/app.py` | source | `SEC-H2`: `Static(..., markup=False)` at the sink; `darkside.plain` on the quoted title at the source |
| `tests/test_confirm_markup.py` | test | **new** — the markup arm, the coercion arm, the oracle RED-proof |
| `.dev-flow/state.json` | doc | item-3 record; `B-64` census correction; the returned judgements |
| `.dev-flow/…/increment-018-item3-pickups.md` | doc | this packet |

| Count | Value |
|---|---|
| **SOURCE files** | **1 / 4** (`mapper/app.py`) |
| Test files | 1 (uncapped) |

---

## 3 · How to test

```bash
cd C:/Users/jjgh8/Github/mapper
set PYTHONUTF8=1 && set PYTHONIOENCODING=utf-8
python -m pytest -q                       # read the SUMMARY line, not the tail
python -m pytest tests/test_confirm_markup.py -q
```

---

## 4 · Test results

| Lane | Exit | Summary |
|---|---|---|
| default | **0** | `1143 passed, 20 deselected, 3 xfailed in 383.16s` |
| slow | **0** | `19 passed, 1147 deselected` |
| network | **0** | `1 passed, 1165 deselected` |
| ruff | — | **27, SETS EQUAL AT EQUAL SCOPE**, both parses asserted non-empty |

`post = base − deleted + added` → **`1143 = 1140 − 0 + 3`** ✓

> **Catalog entry 35 fired on me and is recorded rather than quietly re-run.** The first attempt
> to read this lane used `2>&1 | tail -3`; Textual's `Task was destroyed but it is pending!`
> teardown noise flooded the tail and **pushed the summary line out of view entirely**. *A
> summary line you cannot see is not a green lane.* Re-read with stderr separated and the
> summary matched explicitly, plus the pytest exit code read from the pipeline rather than
> inferred.

### Mutation battery — `SEC-H2`, each half fired SEPARATELY

| Site | Expect | Verdict | Reddened |
|---|---|---|---|
| `H1` sink reverted (`Static` parses markup again) | KILL | **KILLED** | only `…cannot_bind_a_clickable_action` |
| `H2` source reverted (title built raw again) | KILL | **KILLED** | only `…coerces_the_title_it_quotes` |
| `H3` comment-only negative control | SURVIVE | **SURVIVED** | — |

Restore byte-identical. **Firing the halves separately is the point**: a single mutant killing
both arms would leave it unknown whether either arm pins its own hazard.

### Instrument RED-proof

| Instrument | Known-bad input | What it reported |
|---|---|---|
| the painted-frame oracle | `markup=True` vs `markup=False`, same payload | `'xActay'` vs `'x[@click=screen.confirm]Acta[/]y'` — built against BOTH forms before either arm was believed |
| the first oracle (DISCARDED) | `Static.renderable` | `AttributeError` — no such attribute on Textual 8.2.8. **A RED for the wrong reason proves nothing**, so the oracle was rebuilt against the frame rather than the stored content |
| the `B-64` AST census | grep's counts, in both directions | resolved all three divergences (two `escape` on one line; prose counted as code; `saxutils`/`re` correctly excluded) |
| the `B-64` sweep | the hostile title through `darkside.plain` | survivors `none`, U+FFFD present — and the raw fixture asserted to still carry the points, so the probe can see them |

---

## 4b · Independent review

| Field | Value |
|---|---|
| **Independent review** | **OWED for `SEC-H2`.** `qa-reviewer` and `ux-reviewer` returned on the routed pickups (below) but neither reviewed `SEC-H2`; `ux-reviewer` explicitly recorded it as *"not reviewed — security's"*. The `code-reviewer` pass for increment 017 was dispatched against `046acea` and **does not extend to `3ef067c`**. |

---

## 5 · The pickups, as returned

### `F3` → `qa-reviewer`: STILL LIVE, and the original scope judgement is VINDICATED

Re-measured on the current tree (the finding's `radial.py:221` no longer exists; the site is now
`radial.py:298`). The structural statement holds verbatim: **exactly one of four fixture members
has its drawn-ness pinned**. Co-drops of `root`, `first` and `hit` each **survive the 50-arm file
and the whole default lane**; only `other` is killed.

- **Exposure is `RadialRenderer` only**, and it is one of the three renderers `app.py` actually
  constructs. The lane family is constructed nowhere.
- **Inc-W1 was right to decline**, and the measurement strengthens that: the trigger *cannot* be
  asserted from inside `LLR-N07.2.2b` for `root`, because `lane`/`hybrid`/`rail` draw no root
  label at **any** width 80–200 — a design property, not a clip. Owner is the declaration family
  (`HLR-N06.3`), which `01-requirements.md:8974` already records in those words.
- **Remedy recommended: `TC-F3-C`** — per `painted_ids_exporters()` module, assert a 4-node map
  in a 120×24 frame declares every node painted. Kills all four co-drops including `root`.
- **`TC-F3-B` is REFUTED BY MEASUREMENT** and is recorded because it *looks* like the right
  answer: asserting canvas-drawn == `painted_ids` kills **nothing**, because `radial.painted_ids`
  drops the node in lock-step with the canvas — `False == False` one level up.

### `F7` + `UI-AT058` → `ux-reviewer`: one ruling, two NEW findings

- **`F7`: RULED — the precedence stays.** The hit/non-hit answer at the cursor already ships on a
  second channel that costs no cells (the strip's `at/N`, measured `0/5` with the cursor on a
  non-hit). The signal moved; it is not lost. **But `LLR-N07.2.2b` is unmet as written** — its
  *"distinguishably from non-hit nodes"* quantifies over all nodes with no exception for the
  cursor. **The requirement is what is wrong, not the code**, and an amendment is owed.
- **`UX-F7b` — NEW, MEDIUM, and worse than `F7`.** `layered.py:703` paints the unfocused
  selection byte-identically to the hit style. Driven: **six titles in hit livery, five declared
  hits, and the strip in the same frame saying `0/5`**. `F7` withholds a signal the strip
  replaces; this **paints a false one**, with no compensating channel.
- **`UI-AT058`: PASS with two upheld notices** — *"no disponible"* is the Spanish outage idiom and
  invites waiting out a permanent code defect; and *"declaración"* names an internal contract
  where every neighbour names something about the operator's map.
- **`PAN_INERT_HINT`: PASS**, nothing to change.
- **`UX-HINT1` — NEW, LOW-MED.** `_clear_pan_hint` calls `set_hint("")` and `HintLine` has no
  default, so one inert pan press in outline **permanently blanks the hint line in layered too**.
- **The export refusal toast: RULED, the path stays — and my §5 risk from increment 017 is
  measured FALSE.** Driven through real `notify` → real `Toast` → compositor at 6 sizes: the
  actionable half (`Enfoca un subárbol con f…`) paints **intact at every size down to 80×10**,
  because `ToastRack` is bottom-docked so an over-tall toast clips at the **top**. What it does
  cost is real: the toast roughly doubles in height, and at 80×10 it clips away the *headline*.

---

## 6 · Pending items — SURFACED, not fixed

1. **`B-64`'s census is stale (45 derived vs 38 recorded, and a file it never names).** The carry
   travels with its measurements, and the population has moved. Needs re-basing before the
   post-merge cleanup acts on it.
2. **`B-64`'s leak is confirmed outside `lane.py`** (`app.py:511`). The carry's boundary is
   closed in the bad direction; the remedy remains the post-merge body.
3. **`UX-F7b`** — MEDIUM, fix owed, criterion prescribed by the reviewer (*no node outside
   `state.hits` is painted with the hit style in any frame*); the style is not prescribed.
4. **`UX-HINT1`** — LOW-MED, fix owed.
5. **`LLR-N07.2.2b` amendment owed** — the `F7` ruling and the requirement cannot both stand.
   **Coordinator's call, not the implementer's.**
6. **`TC-F3-C`** — the recommended `F3` remedy, not implemented here.
7. **Two test-evidence gaps from the ux pass.** `N-C2`: both refusal arms stub `screen.notify`
   and assert on the message *string* — a pre-layout proxy in `C-32`'s exact sense, blind to
   footprint and clipping. `N-A4`: `"declaración no disponible"` appears **zero** times in
   `tests/`.
8. **A question routed to the coordinator, from the ux pass:** *is the absolute path in the
   refusal toast there for the operator or for a bug report?* If the former, may
   `test_export_state.py`'s arm be re-scoped from "contains the absolute path" to "identifies the
   stale file"? The reviewer declined to rule it because **weakening an acceptance criterion is
   not a reviewer's to do** — which is the asymmetry principle, correctly applied against itself.
9. **`SEC-H2` is owed an independent review.**
10. Unchanged carries: `FLAKE-1` (needs the failing ORDER), `.gitattributes`/`autocrlf`
    (post-merge, `-text`), the socket-level guard, `SEC-F4`, `N3`, `S-F12`, `S-F15`, `N5`/`N6`.

---

## 7 · A provisioning defect in MY mirrors — both reviewers hit it independently

Catalog entry 15 was honoured this round: three reviewers, three private filesystem mirrors, each
digest-verified byte-exact against source (91 `.py` files). **But a mirror of
`mapper/ + tests/ + pyproject.toml` cannot run the lane**, and both reviewers found it:

- `test_a3_census::tracked` shells `git ls-files`, so collection **ERRORS** in a non-git mirror.
- `docs/`, `fixtures/`, `maps/` and `.dev-flow/` are absent; the lane reads all four.

So *"reviewed in an isolated mirror"* and *"ran the lane"* could not both be true of the mirrors
as I provisioned them. `qa-reviewer` closed it with `git init` + `git add -A` **inside** the
mirror, keeping the derivation driven. **Recorded as a third extension to entry 15**: a mirror
must be provisioned against what the LANE reads, not against what the DIFF touches.

**One correction to my own brief, from `qa-reviewer`:** the CRLF list I supplied was incomplete —
`radial.py`, `outline.py` and `layered.py` are also CRLF, while `lane.py` and `test_views_hits.py`
are LF. A `\n` anchor at `radial.py` matches 0×.

---

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | ≤4 source files | ✓ | 1 / 4 |
| 2 | Tests written in this increment | ✓ | 3 arms, written BEFORE the fix and captured RED on the real defect |
| 4 | **RED counterfactual** | ✓ | RED-before-fix captured; battery 3 sites, halves fired separately |
| 5 | **Reverse census** | ✓ | `_ConfirmScreen` has exactly ONE caller (`app.py:3840`), so the sink fix is total |
| 6 | `code-reviewer` passed | **✗ OWED** | §4b |
| 9 | Coverage claims verified on disk | ✓ | every figure measured this session |
| 11 | **Mutation verdicts** per arm | ✓ | §4 |
| 12 | **Instrument RED-proof** | ✓ | §4 — including one oracle DISCARDED for failing in the wrong way |
| 15 | **Independent review** names somebody | **✗ OWED for `SEC-H2`** | qa and ux returned on the pickups only |
| 16 | **Evidence files** | ⚠ | `none — batch declares no artifact_homes.evidence`; inherited gap |
