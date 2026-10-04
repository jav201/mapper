"""`LLR-COERCE.2`'s acceptance-level invariant: COERCED **and** WITHIN BUDGET.

Added by the coordinator's re-ruling of 2026-09-11 -- ADDED, not substituted: the
ordering clause stands as the normative mechanism, and this is the armed
observable beside it. The pairing is the point. A future change to
`darkside.plain` that breaks the order-equivalence assumption on some surface
where nobody is watching the ordering clause is still caught here, because the
budget is measured on the output.

**THE BUDGET IS THE LOAD-BEARING CONJUNCT, AND THE OTHER ONE CANNOT REPLACE IT.**
`out == plain(out)` is *structurally incapable* of detecting a reversed order: any
truncate-then-coerce output ends in a coercion and `plain` is idempotent, so it is
a fixed point BY CONSTRUCTION. An earlier amendment tried to carry the whole
clause on that half; confirmation pass 3 measured it strictly weaker.

WHY THE ORDER MATTERS AT ALL -- the fact that broke a ratified amendment:
`darkside.plain` is index-preserving in CODE POINTS but NOT in DISPLAY CELLS.
**221 of the 235** banned code points have cell width **0**; `U+FFFD` has cell
width **1**. Coercion therefore INFLATES width. `darkside.fit` truncates by
`Text.cell_len`, so coercing after the cut budgets the deflated string and then
inflates it past the budget. The two length-based truncators (`layered._clip`,
`layered._fit`) are genuinely order-equivalent -- which is exactly the trap: a
probe that modelled one of them measured "no difference" and generalised it over
all three.

Code points are NAMED, never pasted (`C-56`).
"""
from __future__ import annotations

import pytest
from rich.text import Text

from mapper import darkside
from tests.test_inc3_census import truncators

ZWSP = chr(0x200B)      # U+200B ZERO WIDTH SPACE -- banned, cell width 0
RLO = chr(0x202E)       # U+202E RIGHT-TO-LEFT OVERRIDE -- banned, cell width 0
SHY = chr(0x00AD)       # U+00AD SOFT HYPHEN -- banned, cell width 1


def cells(s: str) -> int:
    return Text(s).cell_len


def test_the_minimal_witness_two_characters_at_width_one():
    """THE NAMED CASE the re-ruling requires, and the whole argument in miniature.

    `U+200B` + `"A"` at width 1: the specified order emits **1** cell, the
    forbidden order **2** -- 200% of budget from a two-character input. Every
    larger overrun in the record (up to 11x) is this mechanism scaled.
    """
    src = ZWSP + "A"
    assert cells(src) == 1, "the source must already fit, or the arm proves nothing"

    out = darkside.fit(src, 1)
    assert cells(out) <= 1, (
        f"`darkside.fit` emitted {cells(out)} cells into a budget of 1 from a "
        f"two-character source. Coercion inflates a zero-width banned point to "
        "one cell, so truncating before coercing overruns"
    )


def _metric_of(function) -> str:
    """Which unit does THIS truncator budget in -- cells or code points?

    DERIVED BY PROBING, not hand-listed, and not assumed. A wide character costs
    two cells and one code point, so a run of them at a fixed budget separates
    the families: driven at width 5, `darkside.fit` emits 3 code points / 5 cells
    and `layered._clip` emits 4 / 8.

    THE FIRST PROBE HERE WAS WRONG AND THE NON-VACUITY GUARD CAUGHT IT. It asked
    whether a budget of 2 yielded ONE code point; `darkside.fit` answers `' …'`,
    two code points, so every truncator classified as `codepoints` and the
    per-truncator oracle became a constant wearing a derivation. The guard at the
    end of the arm below is what reported it.

    THIS FUNCTION EXISTS BECAUSE THE FIRST VERSION OF THIS ARM ASSERTED CELLS
    AGAINST EVERY TRUNCATOR AND FAILED -- correctly, but against the wrong
    oracle. `layered._vis_width`'s own docstring reads "Approximate visible width
    (simple: length, no CJK handling)", so `_clip`'s budget is CODE POINTS **by
    declaration**. Asserting cells there measures a documented approximation and
    calls it a defect. Each truncator is held to what it claims; the gap between
    what `_clip` claims and what a painted surface needs is a real finding and is
    routed as `B-62`, not smuggled in as a red arm here.

    THE PROBE'S SOURCE IS DELIBERATELY BENIGN -- four CJK code points, no banned
    points -- so the two coercion orders are identical on it by construction. A
    coercion-ordering mutant therefore CANNOT reclassify its way out of the
    oracle below: verified under a mutant running the forbidden order,
    `darkside.fit` still reports `cells` while overrunning its budget. That
    immunity is what makes the per-truncator oracle safe rather than merely
    derived.
    """
    wide = "\u4f60\u597d\u4e16\u754c"      # 4 code points, 8 cells
    out = function(wide, 5)
    if cells(out) <= 5:
        return "cells"
    assert len(out) <= 5, (
        f"{function!r} respected NEITHER metric at width 5: len={len(out)}, "
        f"cells={cells(out)}. The probe cannot classify it, so the oracle below "
        "would be guessing"
    )
    return "codepoints"


def _width_in(metric: str, s: str) -> int:
    return cells(s) if metric == "cells" else len(s)


@pytest.mark.parametrize("width", (1, 2, 3, 5, 8, 13, 20, 40))
def test_every_derived_truncator_stays_within_its_budget(width):
    """THE DERIVED SET, never a hand-listed one -- and never a model of it.

    This arm exists because a hand-built MODEL of one truncator was measured and
    generalised over the clause's three, which is how a false "the orders are the
    same function" reached a ratified requirement. `truncators()` derives the set
    from the tracked sources, so a fourth truncator is covered the day it ships
    and a model of one cannot stand in for all.

    Each truncator is measured in ITS OWN declared unit, itself derived (see
    `_metric_of`). That is not a weakening, and the reason is NOT that the
    defect shows up in every metric -- IT DOES NOT. A reversed order is
    INVISIBLE to a code-point budget, precisely because `plain` leaves the
    code-point count unchanged: measured over 4 hostile sources x widths 1..40,
    0 of 160 forbidden-order `_clip` outputs exceed their code-point budget and
    all 160 are byte-identical to the specified order, while the same sweep run
    against `darkside.fit` -- the truncator held to CELLS -- breaches 114 of 160.
    That control is what makes the zero evidence rather than a blind probe.
    It is not a weakening because `darkside.fit` is the ONLY truncator
    whose order can differ at all, and it is the one held to CELLS. The metric
    each truncator is held to is the metric in which its own reversal would
    show.
    """
    derived = truncators()
    assert derived, "the derived truncator set is empty -- the arm would be vacuous"

    sources = {
        "zero-width prefix": ZWSP * 6 + "abcdefgh",
        "zero-width interleaved": "".join(c + ZWSP for c in "abcdefgh"),
        "balanced override": "aaaa" + RLO + "b" * 30 + chr(0x202C),
        "width-1 banned": SHY * 6 + "abcdefgh",
        "benign": "abcdefghijklmnopqrstuvwxyz",
    }

    seen = set()
    for tname, function in derived.items():
        metric = _metric_of(function)
        seen.add(metric)
        for sname, src in sources.items():
            out = function(src, width)
            got = _width_in(metric, out)
            assert got <= width, (
                f"{tname} emitted {got} {metric} into a budget of {width} on the "
                f"{sname!r} source. Coercion inflates zero-width banned points, "
                "so a truncator that cuts before it coerces overruns its own "
                "budget"
            )

    # NON-VACUITY ON THE DERIVATION ITSELF: the probe must actually be
    # separating a family, not answering the same way for everything by accident.
    assert seen == {"cells", "codepoints"}, (
        f"every derived truncator reports the same metric {seen}. `_metric_of` "
        "is no longer discriminating, so the per-truncator oracle above is a "
        "constant wearing a derivation"
    )


@pytest.mark.parametrize("width", (1, 2, 3, 5, 8, 13, 20, 40))
def test_every_derived_truncator_emits_a_fixed_point_of_its_own_coercion(width):
    """The SECOND conjunct, and it is deliberately the weaker one.

    Kept because it catches a class the budget does not -- a banned point mapped
    to a DIFFERENT banned point rather than to `U+FFFD` passes every length and
    cell check and fails this. It is NOT kept as evidence about ordering, which
    it cannot give: a truncate-then-coerce output is a fixed point by
    construction.
    """
    for tname, function in truncators().items():
        for src in (ZWSP * 6 + "abcdefgh",
                    "aaaa" + RLO + "b" * 30 + chr(0x202C),
                    SHY * 6 + "abcdefgh"):
            out = function(src, width)
            assert out == darkside.plain(out), (
                f"{tname} at width {width} emitted text that is not a fixed "
                "point of its own coercion"
            )
