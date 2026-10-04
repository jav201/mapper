# Inc-REPAIR S-A — Independent Code Review

**Reviewer:** code-reviewer (sole gate, lighter lane)
**Range:** `git diff 5106cee..317c1a9 -- mapper/ tests/`
**Files:** `mapper/darkside.py`, `mapper/widgets/chrome.py`, `tests/test_crumb.py`, `tests/test_a3_census.py`
**Tree at review:** clean at `317c1a9`; byte-identical at exit (shas verified, `__pycache__` purged)

## VERDICT: **PASS** — no HIGH. Six findings, all recommendations.

The fix is correct and the two new arms are not vacuous — both were killed by mutants
that reproduce the exact defects they name. The de-duplication is **complete in
production code**: exactly one numeric `118` literal survives anywhere in `mapper/`.
Full suite: **988 passed, 19 deselected, 3 xfailed**.

Findings F1–F3 are MEDIUM and none blocks. I am not returning a HIGH, and I want the
reason on the record rather than inferred: no finding here is a correctness bug, a data
risk, or a test that gives false confidence. The two arms that matter both discriminate.

---

## What I FIRED vs what I REASONED about

Everything below labelled FIRED was executed. Mutants were CRLF-anchored with the match
count asserted before writing (both files are pure CRLF: 539 / 174 pairs, zero bare LF),
restored by byte-for-byte rewrite with sha re-verified, `__pycache__` purged between runs.
Exit ≥ 2 was treated as a bad mutant; none occurred.

| # | Mutant | Result |
|---|---|---|
| M1 | Revert `__init__` to the pre-fix width-less call | **KILLED** — SEC-F1 arm fails at 30, 40 **and** 60, reporting `97 cells` |
| M2 | Put the literal back in `_crumb_line` (the original drift) | **KILLED** — census arm reports `spelled 2 times` |
| M3 | Plant a `118` literal in `mapper/app.py` | **SURVIVED** — see F1 |
| M4 | Neuter `TabStrip.on_mount` to `pass` | **SURVIVED** — see F3 |
| M5 | Break TabStrip's app rung only (KeyBar untouched) | **KILLED** — SEC-F1 arm binds the rung that matters |

---

## SPECIFIC 1 — The alias question. **RULED: the defence fails. Remove it.**

`mapper/widgets/chrome.py:20` — `_KEYBAR_FALLBACK_CELLS = darkside.DECLARED_CONTEXT_CELLS`

**Your defence is correct on the axis it argues, and that axis is not the one that
decides it.** It is genuinely an import-alias: one value, one home, evaluated once at
import, and it cannot hold a different number. M2 further shows that if anyone
re-literalises it, the new census arm catches it. On **drift**, you are right.

It fails on two other things, both checkable, and I checked both:

**(a) The stated justification is false on both halves.** You kept the name because
"`KeyBar`'s docstring reasoning and test arms reference it."

- *No test arm references it.* The only two hits in `tests/` are `test_crumb.py:277` (a
  `#` comment) and `test_crumb.py:325` (a docstring). Both are **prose**. No test
  imports the symbol, binds it, or asserts on it. `grep -rn "_KEYBAR_FALLBACK_CELLS"
  tests/ --include=*.py` returns those two prose lines and nothing else.
- *`KeyBar`'s docstring does not mention it.* `chrome.py:76-104` refers to "the 118
  default" and "the 118-cell render" — never the identifier. Every occurrence of the
  identifier in `chrome.py` is code: lines 20, 55, 59, 121, 128.

So the cost of deleting it, as stated, is zero. The premise did not survive checking.

**(b) This diff made the name a lie about its own scope.** Before the diff,
`_KEYBAR_FALLBACK_CELLS` was used only by `KeyBar`. After it, **two of its four use
sites are `TabStrip`** (lines 55, 59). It is no longer the keybar's fallback; it is the
module's. A reader who greps the concept now finds two identifiers, one of which names
the wrong widget.

**The right shape:** delete line 20 and reference `darkside.DECLARED_CONTEXT_CELLS`
directly at lines 55, 59, 121, 128. `darkside` is already imported at `chrome.py:10`, so
this costs nothing and removes both the second name and the stale prefix. One concept,
one identifier, spelled where it is used.

---

## SPECIFIC 2 — The spelling census, re-derived independently

I did not read your arm before deriving this. I walked the AST of **every** `.py` under
`mapper/` (not the two files), counting `ast.Constant` nodes whose value equals `118`,
excluding bools, and separately hunting string `"118"` and name/attribute references.

**FIRED. Result — the production de-duplication is complete and correct:**

```
numeric-118 literals in mapper/ (entire package):  1
    mapper/darkside.py:287   DECLARED_CONTEXT_CELLS = 118
string "118" anywhere in mapper/:                  none
```

Reference sites resolve to that one home: `darkside.py:223` (`_crumb_line`), `:293`
(`keybar`'s default), `chrome.py:20, 55, 59, 121, 128`. **No fourth spelling survives.**

**Your AST rewrite is itself correct on the point it was rewritten for.** Docstrings are
`ast.Constant` nodes but their value is a `str`, so `value == 118` excludes them;
comments never enter the AST at all. The prose problem is genuinely solved — raw text
`grep "118"` over `mapper/` returns **25** hits, of which 24 are prose and 1 is the
literal. Your regex-vs-AST correction was the right call and I can confirm the ratio is
worse than the 8-and-5 you first saw.

**Two things the census does not do — one of them matters (F1 below).**

Also worth knowing before anyone "tidies" it: `mapper/app.py:1215` and
`mapper/widgets/rail.py:37` say the layout "auto-hides below 118 columns". That 118 is
**not** the declared context — it is `MIN_CANVAS_WIDTH (58) + RAIL_WIDTH (24) +
INSPECTOR_WIDTH (36) = 118`, a derived threshold that collides numerically by accident.
Do not fold it into `DECLARED_CONTEXT_CELLS`. They are two different 118s.

---

## Findings

### F1 — Census population is two modules, not `mapper/` [MEDIUM]
**Where:** `tests/test_crumb.py:335-355` (the `for name, mod in (("darkside.py", _d), ("chrome.py", _c))` loop)

**What:** The arm scans exactly two modules. Its docstring claims "The declared context
has **ONE home**, and this is what pins it" — it pins two files.

**FIRED (M3):** I planted `_PLANTED_FALLBACK = 118` in `mapper/app.py` beside
`MIN_CANVAS_WIDTH`. `test_decl_118_is_spelled_ONCE` **stayed green** (exit 0, 1 passed).
A fourth spelling in any other module is invisible to the arm that exists to forbid it.

**Why it matters:** The carry recorded two spellings and there were three — the arm's own
docstring makes that its headline lesson. An arm whose population is "the modules I
happened to be editing" will repeat exactly that miss the next time the number leaks into
a module nobody was looking at. Today the census is clean; the arm is what keeps it clean.

**Smallest fix:**
```python
import mapper
spellings = {}
for path in sorted(Path(mapper.__file__).parent.rglob("*.py")):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    hits = [n.lineno for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and not isinstance(n.value, bool)
            and isinstance(n.value, (int, float)) and n.value == 118]
    if hits:
        spellings[path.name] = hits
```
I ran this exact population against the pristine tree: total **1**, so it passes today and
would have killed M3.

---

### F2 — Remove the alias [MEDIUM]
**Where:** `mapper/widgets/chrome.py:20`, used at `:55, :59, :121, :128`
Ruled in full under **Specific 1**. Fix: delete line 20; use `darkside.DECLARED_CONTEXT_CELLS`
at the four sites.

**Why it matters:** not drift — you are right that it cannot drift — but a second name for
one concept, carrying a `KEYBAR` prefix that this diff falsified by giving it a second
consumer.

---

### F3 — `TabStrip.on_mount` is added mechanism that nothing pins [MEDIUM]
**Where:** `mapper/widgets/chrome.py:61-65`

**FIRED (M4):** Replaced the `on_mount` body with `pass`. `tests/test_crumb.py`,
`tests/test_strips.py` and `tests/test_a3_census.py` — **39 passed, 0 failed**. The suite
cannot tell whether this method exists.

**Why it matters:** Its own comment makes a claim — "this render does not depend on a size
CHANGE ever happening" — and no arm exercises a case where the change does not happen. This
is control 18's shape exactly: the belt is justified by a scenario the suite never enters,
so we cannot distinguish "the belt works" from "the belt is inert". I note honestly that
`KeyBar` shipped the same unpinned belt at `Inc-CRUMB`, so this is consistent with
precedent rather than a new sin — which is why it is a recommendation, not a block.

**Smallest fix:** one arm that suppresses the correction path and asserts the invariant
the comment claims:
```python
async def test_the_mounted_strip_is_bounded_WITHOUT_a_resize(tmp_path, monkeypatch):
    monkeypatch.setattr(TabStrip, "on_resize", lambda self: None)
    # mount, then assert the held crumb row is <= the app width
```
That arm fails if `on_mount` is removed and passes today.

**Separately — the double-render question you asked, answered by measurement, no defect
found.** FIRED: I spied `darkside.tab_strip` through a real `MapperApp` run.

```
size=(30,20):  startup calls = 3, widths = [30, 30, 30]   | one resize -> +1 call (40)
size=(118,34): startup calls = 3, widths = [118,118,118]   | one resize -> +1 call (128)
size=(80,24):  startup calls = 3, widths = [80, 80, 80]    | one resize -> +1 call (90)
```
`on_mount` **does not fight** `on_resize` — all three startup renders agree on the same
correct width, and one resize produces exactly one further render. No oscillation, no
storm. Note also that the **constructor** render already gets the true width (30, not 118),
so the app rung resolves during `compose` in the live path, not only under test.

---

### F4 — The `_width()` ladder is duplicated verbatim [MEDIUM]
**Where:** `mapper/widgets/chrome.py:52-59` vs `:118-128`

**What:** Same three rungs, same `NoActiveAppError` branch, same fallback — eight lines,
differing only in comment text.

**Ruling on the tension you flagged** (control against second spellings vs control against
second mechanisms): this is a second spelling of a **policy**, and the policy is the thing
the increment just spent itself de-duplicating one level down. Having given the *number*
one home, leaving the *rule that consumes it* written twice is the same defect at a higher
altitude.

**The honest mitigation, which is why this is the weakest of the three MEDIUMs:** both
copies are currently arm-pinned. M5 broke TabStrip's app rung alone and the SEC-F1 arm
killed it, so a one-sided edit today would be caught. The cost is a future rung: add a
fourth step to one ladder and the other silently keeps three, with no arm comparing them.

**Smallest fix:** a module-level free function, least coupling of the options:
```python
def _resolved_width(widget) -> int:
    """Widget's own width, then the app's, then the declared context."""
    if widget.size.width:
        return widget.size.width
    try:
        return widget.app.size.width or darkside.DECLARED_CONTEXT_CELLS
    except NoActiveAppError:
        return darkside.DECLARED_CONTEXT_CELLS
```
Both `_width` methods become `return _resolved_width(self)`, keeping their distinct
docstrings. This also absorbs F2 at no extra cost.

---

### F5 — The "97 cells at 30, 40 AND 60 columns" claim overstates its own evidence [LOW]
**Where:** `mapper/widgets/chrome.py:43-45`

**FIRED — the number is right.** Calling `darkside.tab_strip("c", crumb)` with no width
(exactly the pre-fix constructor) on the arm's own fixture yields a crumb row of **97
cells**, and `_crumb_line(crumb, 0)` is likewise **97**. Confirmed. The conclusion —
"a budget ignoring the terminal" — is also right.

**The framing is not.** "97 cells of crumb at 30, 40 **AND** 60 columns, identical at all
three" reads as three measurements at three terminal widths that converged on one answer.
There were never three. The pre-fix constructor passed **no width at all**, so
`_crumb_line` took its fallback and produced one width-independent value. "Identical at
all three" is a tautology of the call site presented as an empirical finding. Post-fix, by
contrast, the three widths genuinely differ: 29 / 35 / 35 cells at 30 / 40 / 60.

**Why it matters:** this is the calibration you warned me about — measurement sound,
explanation inflated. A reader who trusts the sentence believes the terminal width was
varied and found not to matter, which would point at `_crumb_line` as the bug. The bug was
at the call site.

**Smallest fix:** "Measured before the fix: the constructor passed no width at all, so
`_crumb_line` took its 118-cell fallback and rendered 97 cells of crumb regardless of the
terminal — identical at 30, 40 and 60 because the terminal was never consulted."

---

### F6 — Dead guard in the census comprehension [LOW]
**Where:** `tests/test_crumb.py:347-348`

`isinstance(node, ast.Constant) and node.value == 118 and not isinstance(node.value, bool)`
— `True == 118` and `False == 118` are both `False`, so the bool guard can never fire. It
reads as protecting against something it cannot encounter.

**Smallest fix:** reorder so the guard is load-bearing:
`isinstance(n.value, (int, float)) and not isinstance(n.value, bool) and n.value == 118`
(this also keeps `118.0` counted, which `== 118` already does).

---

### F7 — Two LOW notes, grouped [LOW]

**(a) The constant sits below its first consumer.** `DECLARED_CONTEXT_CELLS` is defined at
`darkside.py:287`; `_crumb_line` reads it at `:223`. It works — module-global lookup is at
call time, and `keybar`'s def-time default at `:293` is safely after it (verified:
`inspect.signature(keybar).parameters['width'].default` is the same `int` object). But it
breaks the module's own local convention, where `_CRUMB_SEP_CELLS` / `_CRUMB_DROP_CELLS` /
`_CRUMB_TAIL_MIN_CELLS` sit immediately **above** `_crumb_line`. A reader of `_crumb_line`
meets a name with no definition above it. Fix: move the constant and its comment above
`_crumb_line`.

**(b) "the ONE place it is written" over-claims repo-wide.** `darkside.py:274` says "The
batch's DECLARED CONTEXT OF USE, and the ONE place it is written". True for production
code and for the fallback budget. Not true of the declared context of use as such: the
suite spells `(118, 34)` independently at `test_pan.py:32`, `test_fold.py:33`,
`test_search.py:45`, `test_crumb.py:33`, `test_strips.py:52`, plus inline at 10+ call
sites. Fix: narrow to "the one place the fallback **budget** is written". I am **not**
asking for the test-side constant to be unified — that is a different concern and out of
this increment's scope.

---

## Things I checked and found CLEAN

- **`keybar`'s default-parameter change is behaviourally inert.** Evaluated at def time
  against a constant defined 6 lines earlier; the default is the identical interned `int`
  `118`. Callers passing nothing are unaffected; there is no import-order hazard because
  the constant precedes the `def`. FIRED via `inspect.signature`.
- **The SEC-F1 arm reads what it claims** — the constructor's render, not a rescued frame.
  M1's failure message is `budgeted the crumb against 97 cells`, the exact pre-fix value,
  proving it sees the constructor's output. It also reads the **right row**:
  `tab_strip` returns `Text.assemble(line, "\n", _crumb_line(...))`, so `split("\n")[1]`
  is the crumb by construction, and the `assert crumb_row` vacuity guard is real.
- **All three SEC-F1 parametrisations discriminate** (M1 killed 30, 40 and 60), because
  the pre-fix 97 exceeds all three budgets. The 30-column case is the strongest: post-fix
  it yields 29 cells against a 30-cell lid, so a wrong-but-smaller budget would still be
  caught there.
- **A3 census bump 28 → 29** is honest — both pinned arms derive 29 and pass.
- **No evidence of another writer.** Working tree clean at entry and exit; `git status`
  empty; `mapper/darkside.py`, `mapper/widgets/chrome.py` and `mapper/app.py` all match
  their pristine sha256 after every mutant.

## Boundaries

- **Reviewed:** the full four-file diff `5106cee..317c1a9`, read in full; plus a repo-wide
  AST census over `mapper/` and `tests/`; plus five mutants; plus a live-app render count.
- **Did not review:** security (out of lane and waived for this stage), suite-wide
  functional/UX validation beyond the confirmation run, performance.
- **Could not determine:** whether `on_mount` has live value in a real terminal. Under
  `run_test` the corrective resize always fires, so I measured only a world in which the
  belt is redundant. F3 asks for the arm that would settle it; I did not construct a
  scenario proving the belt is load-bearing outside tests, and I do not claim one exists.

**Verdict: PASS.** F1–F4 are worth taking before the batch closes; F5–F7 are prose and
tidying. None restores full protocol.
