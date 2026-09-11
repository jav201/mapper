# Increment 012 — `Inc-REPAIR` S-E · the sidecar's shipped defects and the coercion sink beside them

**Status:** security review folded. The `BLOCK` is cleared — the review named **`SEC-H1` alone** as
the block, it is fixed and witnessed by mutation, and `SEC-M1`'s missing arm is fixed and witnessed
too. `SEC-H2` is a HIGH this gate **found out of diff**; it is routed to `Inc-CONFIRM`, **not**
fixed and **not** witnessed here.

`AT-049` (`B-29`, `LLR-REPAIR.1`) · `AT-050` (`B-30`, `LLR-REPAIR.2`) · `B-48` (the attachments
phantom) · `LLR-N13.1.7` (alias amplification) · the `screens/coverage.py` coercion sink.

## What S-E is

`AT-049` and `AT-050` **had no nodes on disk.** They were ratified in `01-requirements.md` §3.9 and
never written — the `AT-005`/`AT-006` shape this batch already carries, found at the pre-gate before
any fix. `tests/test_repair_sidecar.py` is `AT-050`'s whole home and the STORE half of `AT-049` (see
below), and it also carries the two amplification arms and the two coverage-sink arms.

### `AT-049` is discharged at the STORE, not at the CARD — and that is by design, not by omission

The code review flagged this and could not resolve it: *"Whether the `AT-049` pilot arm (`HomeScreen`
damaged card) is deferred by an authority I did not find."* I found the authority, and it does not
say what I would have liked.

`AT-049`'s ratified surface is `#home-recents` — §3.9's boundary catalog asks the positive arm to
assert *"the card enters the damaged state"* and the negative arm *"no warning **and a healthy
card**"*. **Neither card assertion is in this module**, and it cannot be written here: there is no
damaged card state in the code. `HomeScreen` reports a damaged load as a **toast**
(`app.py:546-551`, `app.py:1277-1290`); the recents table has no damaged column and no damaged style.

That is not a gap S-E can close, and §5.4 says why: `LLR-REPAIR.1` **gates `Inc-7`** *"because
without it `AT-025b` is vacuous"*, and `LLR-N13.1.5` identifies the `k` damaged maps *"by the load
path raising or **recording a load warning**, never by a clock"*. The warning this stage adds is the
thing the card will later be painted from. `AT-025b` has no node on disk either — so the card half
of `AT-049` and the containment arm that consumes it land together at `Inc-7`.

**So: `LLR-REPAIR.1`'s warning clause is discharged and witnessed here; `AT-049`'s card clause is
owed by `Inc-7`.** Labelled as partial rather than claimed whole — and labelled **in the test
module's own docstring**, not only here, because the module previously read *"This module is their
home"* for both `AT`s. A future reader would have taken a green run of it as `AT-049` discharged,
which is the declaration-outrunning-the-code failure this batch keeps cataloguing. The docstring now
ends: *"do not read a green run of this module as `AT-049` discharged."*

## The fold

### SEC-H1 — `load_warnings` unbounded · FIXED, WITNESSED

The review measured 20,107,707 characters against a `< 2_000` oracle — **10,053×**, deterministic,
0.06 s. Worse than the record: my own `B-48` fix had *added* the largest amplifier, an
`adjunto sin campos: {owner}…` record with an unbounded `owner` — 2.0 GB in 0.84 s, 9,092×.

Fixed in `mapper/store.py` with a single `_warn(graph, record)` helper carrying **two** bounds, and
**all 11 producers routed through it**:

* `_RECORD_CHARS = 200` — per-record truncation.
* `_MAX_RECORDS = 200` — list cap, with one final record that says the list was capped.

A type bound is not a length bound: `_raw_origin` had a type bound and still fired at 348× from a
57 KB file, so it now truncates at `_ORIGIN_CHARS = 120` rather than being removed — `AT-P02d` needs
the origin.

**I landed ONE of the two bounds the review recommended, and the second is redundant — stated here
rather than left as a silent deviation.** The review asked for a store-side cap *and* a
`_warning_toast` bound at `app.py:548` / `:1287`. With the store cap in place, `store.py:191` and
`:197` — both inside `_warn` — are the **only** two `load_warnings.append` sites in the whole
codebase, re-derived after the whitespace fix moved them; every other
reference reads. So the joined toast body is bounded by arithmetic on the two constants:
`201 × 201` characters plus separators, **under 41 KB**, against the 2.0 GB the review measured. A
second bound at the sink would guard a quantity that can no longer be produced. If a future module
appends outside `store.py`, that reasoning lapses and the sink bound comes back. The review's own
wording allows it — *"cap `load_warnings` at the sink **and/or** at the append"*.

**One row of the review's posture table flips as a side effect.** It rated the new
`nodo fantasma: {nid!r}` **NEUTRAL-to-LOSS** because `nid` is unbounded. Routing it through `_warn`
bounds it at 200 characters like every other producer, so that row is now a **GAIN** too — not
because it was re-argued, but because the sink-side fix covers all eleven producers by construction.
That is the property the helper was chosen for: a twelfth producer cannot reintroduce the class by
spelling its own `append`.

### SEC-H2 — `_ConfirmScreen` executes markup from a ficha title · ROUTED to `Inc-CONFIRM`

Confirmed as `B-46`'s family but **worse than recorded**: `[@click=…]` is executable, `[conceal]`
hides text, and `[/]` crashes the app. The fix needs **both** `darkside.plain` at `app.py:3342` and
`Text(...)` at `app.py:253`.

The census below establishes the blast radius precisely: `app.py:3364` is the **only**
`_ConfirmScreen` call site, and its message is built at `app.py:3342` from
`node.ficha.title or node.id`. All six `_PromptScreen` call sites pass **constant** titles, so the
sibling modal at `app.py:213` is not reachable with file-derived text. One producer, one sink.

### SEC-M1 — the `HIGH-1` fix had no arm · FIXED, WITNESSED

The code review's condition was `Text(...)` **plus** an arm asserting `spans == []`. Only the first
landed, and the review fired the wrap's removal against the whole suite: **997 passed, not one arm
moved.**

**My first replacement arm also survived that mutant**, and the reason is the finding worth keeping:
it built its own subject — `Text(darkside.plain(hostile))` — so it asserted a property of an
expression *it had written*, not of the one `coverage.py` passes. A parallel fiction, the same
failure this batch named for the `AT-058` absent-state arm. An arm that constructs its own subject
cannot see the call site change.

The arm now drives a real `CoverageScreen` under `Pilot` at 118×34, pulls `table.get_row_at(0)`, and
asserts on what the table was actually handed.

**I did not implement the review's suggested arm verbatim, and the reason is the finding above.**
The review's snippet builds `cell = Text(darkside.plain(hostile))` and asserts on that. That is the
shape my first attempt used, and **I fired `M-TXT` against it: it SURVIVED.** An arm that constructs
`Text(plain(x))` itself passes whether or not `coverage.py` still does. The recommendation is right
about the property and wrong about the subject, so the property moved to the real call site.

The review's **second** recommendation — a separate arm for the crash class, since `[/]` is a
different failure mode from a leaked span — is implemented as its own arm rather than folded into
the first.

### SEC-M2 — the coercion-sink census · DONE; it CORRECTS the review's worry, and finds a different defect

The review's concern was that `HIGH-1` might be one of several. **It is not.** The census resolves
every `escape` / `darkside.plain` call site in `mapper/` against its sink:

```
plain at a PARSING sink (the HIGH-1 shape)      0
escape at a parsing sink (correct)              3     app.py:292 ×2, app.py:655
escape at a NON-parsing sink                   38
```

**`plain`-at-a-parsing-sink count is zero.** `screens/coverage.py` was the only instance in the
repo, and it is fixed. SEC-H2 is a *third* idiom — a raw `str` with no coercion at all — and the
census confirms it has exactly one producer.

**Two corrections the first census run needed, both of which had inflated the defect count.** Both
are recorded because a census that quietly self-corrects is not evidence:

* `notify(..., markup=False)` **parses nothing.** The first run flagged six `darkside.plain` calls at
  `self.notify` as the `HIGH-1` shape; every one passes `markup=False`. All six are correct.
* `office.py` imports `escape` from `xml.sax.saxutils`, **not** `rich.markup`. Three sites there are
  XML escaping and are not governed by this rule at all. The census now checks each module's import.

**Boundary.** The census sees syntactic enclosure plus one step of assignment following. It cannot
follow a value through a helper, a container, or a function boundary. Five sites it could not
resolve are named rather than dropped, and were read by hand: `app.py:2656` → `notify(markup=False)`;
`app.py:2978`/`:2979` → crumb and toast, both `Text`; `factory.py:252`/`:350` and `rail.py:230` →
`Text.assemble` parts. All literal. **It does not see runtime reachability** — it is a census of call
sites, not of reachable paths.

#### NEW FINDING · `SEC-M2-a` — `escape` at 38 non-parsing sinks · ROUTED, not fixed here

`darkside.py:266` already **states the rule** this repo needs, and states it correctly:

> `escape` adds a cell per markup-shaped bracket run AFTER the budget has been spent … It was also
> wrong on its own terms. `Text.assemble` with `(str, style)` tuples appends LITERAL text and parses
> no markup, so the backslash was painted on screen rather than protecting anything.

The rule is not applied at 38 sites — including `darkside.py:393` itself, in the module that
documents it. Distribution, derived from the census rather than counted by eye —
`app.py` 14 (ficha modal, home), `factory.py` 12, `lane.py` 7, `editor.py` 4, `darkside.py` 1;
**38 in 5 source files**.

Two costs, one cosmetic and one security-shaped:

1. A `[b]`-bearing title renders a **literal backslash** on screen and **breaches a budget measured
   honestly** — `darkside.py` measured this at seventy of seventy widths from 20 to 89.
2. `escape` performs **no control-byte or bidi coercion**. `darkside.plain` maps `COERCION_RANGES`
   to `U+FFFD`; `escape` does not. So at these 38 sinks, control bytes and right-to-left overrides
   from a sidecar-controlled title reach the screen unsanitised — the exact hazard `plain` exists to
   stop (`app.py:3086`).

**One of the 38 is PINNED.** `tests/test_darkside_census.py` carries
`("mapper/screens/factory.py", 'parts.append((escape(f"{{{{{key}}}}}"), darkside.ALERT))')` in its
expected-sites list, so whoever fixes `SEC-M2-a` re-pins that row in the same change. The hue census
is a census of **declared colour tokens**, not of coercion — it does not cover this class, and no
existing arm does.

**Not fixed in S-E.** It is pre-existing, repo-wide, outside S-E's scope (the sidecar and the
coercion sink beside it), and it would touch **five source files** — over cap on its own. Severity is
**MEDIUM**: display corruption and RTL spoofing, not execution. Sites reached through `darkside.fit`
are already coerced (`fit` calls `plain`), which lowers the real exposure below the raw 38 and is
the reason this is a route and not a block — `layered.py:649` is exactly that case and is **not**
counted in the 38, because its `escape` lands inside a `_fit` call that coerces anyway.

### SEC-M3 — a true number one line past where it is true · FIXED (and my first fix left a residue)

The arm's docstring paired a **pre-fix** figure (522,311 chars) with the words *"Measured on the
shipped tree"*. On the shipped tree the same fixture is **107 chars against a 2,000 bound — 19×
under, not red by four orders of magnitude.**

My first correction added the pre-/post-fix distinction at the top **and left the original
conclusion standing at the bottom**, so the docstring said both things: *19× under its bound* and
*RED by four orders of magnitude*, four lines apart. A self-contradicting docstring is not a
corrected one. Rewritten so a single reading survives: benign 31, shipped 107, and the 261× redness
attributed to the **reintroduced defect**, which is the only thing it was ever true of.

**And I checked the inherited number instead of re-typing it.** My first reproduction interpolated
**both** halves of the duplicate record raw and produced **1,044,465** — twice the figure. The
pre-fix line only ever materialised the second half: `doc.name` is the value the per-key coercion
had already replaced with `''`. Reproduced correctly, the record is **522,247** characters, and the
two `campo ilegible: document[i].name` records are 32 each — **522,311 total**, which is exactly the
review's figure and exactly what the arm's `sum(len(w) for w in ...)` oracle measures. The
decomposition is now in the docstring, so the next person inherits a number with its parts attached.
Had I not checked, I would have shipped a docstring asserting a defect shape that never existed.

## Mutation evidence

Byte-level, CRLF-anchored, match-count asserted before firing, `__pycache__` purged, sha256 restore
verified. Harness: `C:\Users\jjgh8\clde\sech1_verify.py`.

```
BASELINE  11 passed in 0.37s

mutant                         verdict      detail
----------------------------------------------------------------------------
M-REC per-record truncation    KILLED       1 failed, 10 passed in 0.38s
M-CNT list cap                 KILLED       1 failed, 10 passed in 0.38s
M-TXT coverage markup wrap     KILLED       2 failed,  9 passed in 0.74s

RESTORES VERIFIED byte-identical
ALL KILLED
```

`M-TXT` is the one that matters: the security review fired that same mutant against the whole suite
and got **997 passed, not one arm moved.** It now reddens **two** arms, one per failure mode — the
leaked span and the crash.

## Three small items that were not findings

* **`_warn`'s cap message was misspelled Spanish.** `"... y mas registros omitidos (limite 200)"` — no
  accents, an ASCII ellipsis. The batch's own earlier repair review had already written the correct
  form, `"… y más registros omitidos"`, so this now matches that precedent. Operator-visible text;
  no arm asserts on it, checked before changing it.
* **`from rich.text import Text` became unused** once both coverage arms moved their imports inside
  the test functions. Caught by the ruff SET gate, not by eye.

* **Three trailing spaces, introduced by my own `_warn(graph, ` edits — and my first check said the
  file was clean.** `Grep`'s `[ \t]+$` returned **no matches** on `store.py`, because a `$` anchor
  does not see past a `\r` on a CRLF tree. Reading the bytes with `newline=''` found all three.
  Ruff could not see them either (`W291` is not in this repo's selected set), so both of my
  automated checks agreed on a false clean. The three calls are now split across lines with no
  trailing space, verified on bytes.

**One cosmetic residue left deliberately:** the first coverage arm still declares a `tmp_path`
fixture it no longer uses — it builds its `Graph` in memory and writes nothing. Ruff does not flag
it (`ARG001` is not in this repo's selected set) and it is inert, so I did not spend a second
ten-minute three-lane run on a parameter name. Named here rather than left for a reviewer to find.

## Gates

| Gate | Result |
|---|---|
| Default lane (`-m 'not slow'`) | **1000 passed, 19 deselected, 3 xfailed** in 245.45 s · exit 0 |
| Slow lane (`-m slow`) | **19 passed, 1003 deselected** in 52.30 s · exit 0 |
| All markers (`-o addopts=`) | **1019 passed, 3 xfailed** in 301.50 s · exit 0 |
| Ruff SET gate (changed files, `HEAD` vs worktree) | **PASS** — 0 findings added, 1 removed (`I001`) |
| Ruff whole repo | **27** — was 28 before this stage removed the unused import; the batch's recorded baseline is 29 |

**The three lanes agree by arithmetic, which is the check worth stating.** Lane 3 collects
1019 + 3 = **1022**; lane 1's 1000 + 3 plus lane 2's 19 is also **1022**, and lane 2's
19 + 1003 deselected is **1022** again. Three independent runs partition the same collected set with
no residue, so no arm is silently deselected in every lane.

Suite growth: **995** at `ea5d4c2` → **997** at `46075a4` (the code review's two folded arms) →
**1000** here (the rewritten coverage arm, the `[/]` crash arm, and the attachment-amplification
arm).

The SET gate compares finding **sets**, not counts, and asserts the parse count so an empty parse
cannot read as clean. It reads `HEAD` through `git show` into a temp directory — never a checkout —
so no gate reads a tree this workflow wrote.

**A measurement I nearly reported wrong.** My first two lane runs merged stderr into stdout, and
Textual's `Task was destroyed but it is pending!` teardown noise pushed the summary line out of the
tail I was reading. One of those runs showed **no summary at all** and I let it pass; the next run's
exit code 1 came from **ruff**, not pytest, which would have read as a suite failure. Both lanes were
re-run with stdout captured separately. Recorded because the near-miss is the point: a lane whose
summary you cannot see is not a green lane.

## Routed, not fixed here

| Id | Severity | Where it goes |
|---|---|---|
| `SEC-H2` | HIGH | **`Inc-CONFIRM`.** `darkside.plain` at `app.py:3342` **and** `Text(...)` at `app.py:253`. Both. One producer, one sink — the census confirms no others. |
| `SEC-M2-a` | MEDIUM | **New — needs a ruling.** 38 `escape` calls at non-parsing sinks across 5 source files; over cap on its own, and one site is pinned in `test_darkside_census.py`. |
| `AT-049` card clause | — | **`Inc-7`**, with `AT-025b`, which also has no node on disk. The store-level warning this stage adds is what the card is painted from. |
| `SEC-L1` combining marks | LOW | Carried. Adding `Mn` to `COERCION_RANGES` would break legitimate Spanish and indigenous-language titles; NFC + a consecutive-mark cap if anything. |
| `SEC-L2` record forgery in the joined toast | LOW | Carried. Belongs with a sink helper — one record per line, or `repr` at every id interpolation. |
| `SEC-L3` `app.py:939` `Static(self.repo)` | LOW | Carried. Operator-typed, but realistically pasted from a client README. |
| `SEC-L4` `MapStore.load` containment | LOW | Carried. `store.load("../../x")` resolves outside the workspace; every `map_id` traced is a table row key or operator-typed, so it is self-harm, not attacker-controlled. Flagged only because `B-30` changed the adjacent line. One guard: `if Path(map_id).name != map_id: raise`. |
| Sink census as a test arm | MEDIUM | The review's own recommendation: extend the ratified AST-census shape to `Static` / `Label` / `DataTable.add_row`. It needs the exact-stripped-line pin, because a naive walk returns 23 hits of which 21 are helpers returning `Text`. |

**Soft cap reached: 3 items surfaced to the coordinator** — `SEC-H2` (already agreed), `SEC-M2-a`
(new), and the `AT-049` card clause (resolved to `Inc-7` by reading the authority, not by assertion).
