"""`LLR-N06.3.5`'s EMPTY-FRAME FLOOR EXCEPTION, and the proviso that arms it.

The clause says both declaring surfaces speak, agree, and are right. The
exception (amended `S-B(+C)`, coordinator ruling 2026-09-11) lets the renderer's
header be silent WHEN THE DECLARING HEADER CANNOT FIT WITHOUT EVICTING THE LAST
CONTENT ROW -- **provided the strip is present in the same composited frame and
declares the correct count.**

THAT PROVISO IS WHAT THIS MODULE PINS. The exception is conditional, so it can
LAPSE: if a future layout change pushes the strip off-frame at a floor size, or
makes it wrong there, the exception no longer holds and these arms redden.

THE TRIGGER IS DERIVED, NOT ENUMERATED. The floor sizes are not hand-listed --
they are selected by the condition itself (something is hidden, and the canvas
declared nothing). A size list would silently stop matching the day the layout
moved, which is the failure `LLR-N06.3.5`'s own amendment warns about.

AND THE PARSE IS ANCHORED ON THE TOKEN, NOT ON POSITION. The sweep that produced
the eighteen measurements first reported 56 and 50 disagreements, all false: it
took the first number on a line containing "fuera de vista", and the strip reads
`1/8  \u25bd 5 fuera de vista`, so it harvested the PAGINATION POSITION. Every row
said `strip=1` -- and a constant across a sweep is the instrument's signature,
not the world's.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
from textual.widgets import Static

from mapper.app import COUNT_REGION_ID, MapperApp, MapScreen
from mapper.views import outline, radial

WS = Path(__file__).resolve().parent.parent / "fixtures"

# Widths and heights spanning the narrow/short corner and well past it, so the
# derivation has both floor and non-floor frames to separate.
SIZES = [(w, h) for w in (24, 28, 31, 34, 40, 60, 100)
         for h in (10, 12, 14, 16, 20, 30)]

DECLARED = re.compile("\u25bd\\s*(\\d+)")


def _declared(text: str) -> int | None:
    m = DECLARED.search(text)
    return int(m.group(1)) if m else None


async def _frame(map_id: str, size):
    """Canvas declaration, strip declaration, strip presence, and the truth."""
    app = MapperApp(WS)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        app.push_screen(MapScreen(map_id))
        await pilot.pause()
        screen = app.screen
        screen.outline_mode = True
        screen.refresh_canvas()
        await pilot.pause()

        canvas = screen.query_one("#map-canvas", Static)
        strip = screen.query_one(f"#{COUNT_REGION_ID}", Static)
        w, h = screen._canvas_size()
        state = screen._view_state(w, h)
        painted = outline.painted_ids(screen.graph, state)
        rows, _sc = outline._rows(screen.graph, state)
        return {
            "canvas": _declared(canvas.render().plain),
            "strip": _declared(strip.render().plain),
            "strip_on_frame": strip.region.height > 0,
            "truth": len(screen.graph.nodes) - len(painted),
            # THE GEOMETRIC TRIGGER, from the renderer's own predicate.
            "at_floor": outline.floor_reached(rows, w, h),
        }


@pytest.mark.parametrize("map_id", ("legacy", "anidado"))
async def test_at057_floor_the_strip_carries_the_declaration_the_canvas_drops(map_id):
    """THE EXCEPTION'S PROVISO, over every frame the condition selects.

    At a floor frame the canvas is allowed to say nothing. It is NOT allowed to
    say nothing while the strip is also absent or wrong -- that is two surfaces
    agreeing on a falsehood, which the unamended clause forbids and the exception
    never licensed.
    """
    floors = []
    for size in SIZES:
        f = await _frame(map_id, size)
        # SELECTED ON THE TRIGGER, NOT ON THE CONSEQUENCE. This used to skip on
        # `canvas is not None`, i.e. on ANY canvas silence -- which is what the
        # floor CAUSES, not what the floor IS. The code review fired the gap:
        # widening `_fit_declared`'s fallback BEYOND the empty-frame floor left
        # this arm green at 4 passed while the exempted set grew from 9 to 17 on
        # `legacy` and 9 to 14 on `anidado`. Selected that way, the exception
        # could not lapse in the one direction that matters -- silently becoming
        # broader than the requirement licensed.
        if f["truth"] <= 0 or not f["at_floor"]:
            continue                      # not a floor frame; the clause proper applies
        floors.append(size)
        assert f["strip_on_frame"], (
            f"{map_id} at {size}: the canvas declared nothing and the strip is "
            "NOT on the composited frame. The floor exception has LAPSED -- both "
            "surfaces are silent over a frame hiding "
            f"{f['truth']} node(s)"
        )
        assert f["strip"] == f["truth"], (
            f"{map_id} at {size}: canvas silent, strip says {f['strip']}, truth "
            f"is {f['truth']}. The exception requires the strip to be CORRECT, "
            "not merely present"
        )

    # NON-VACUITY. Without this the arm passes by never reaching a floor frame at
    # all -- green because it tested nothing, which is the `C-55` shape this
    # requirement was rewritten to escape in the first place.
    assert floors, (
        f"{map_id}: no floor frame was reached over {len(SIZES)} sizes, so this "
        "arm asserted nothing. Either the sweep no longer spans the narrow/short "
        "corner or the floor is unreachable -- both need a human"
    )


@pytest.mark.parametrize("map_id", ("legacy", "anidado"))
async def test_at057_above_the_floor_the_canvas_still_declares(map_id):
    """THE CONTROL. The exception must not quietly become the general case.

    If the canvas stopped declaring everywhere, the arm above would still pass --
    every frame would look like a floor frame and the strip would still be right.
    So this asserts the unamended clause still governs where it should: at frames
    that hide nodes and are NOT at the floor, the canvas speaks and agrees.
    """
    ordinary = []
    for size in SIZES:
        f = await _frame(map_id, size)
        # ALSO SELECTED ON THE TRIGGER. Skipping `canvas is None` here was the
        # other half of the same hole: it skipped exactly the frames a widened
        # fallback creates, so the pair could not see the exception spread.
        if f["truth"] <= 0 or f["at_floor"]:
            continue
        ordinary.append(size)
        assert f["canvas"] is not None, (
            f"{map_id} at {size}: the canvas is silent on a frame that is NOT at "
            f"the floor and hides {f['truth']} node(s). The exception has spread "
            "beyond what LLR-N06.3.5 licensed"
        )
        assert f["canvas"] == f["truth"] == f["strip"], (
            f"{map_id} at {size}: canvas={f['canvas']} strip={f['strip']} "
            f"truth={f['truth']} -- above the floor all three must match"
        )

    assert ordinary, (
        f"{map_id}: the canvas declared at NO size that hides nodes. The floor "
        "exception has swallowed the general case"
    )


# ---------------------------------------------------------------------------
# RADIAL. `S-D`'s workstream 2, re-scoped by coordinator ruling 2026-09-18 from
# "fix the radial floor" to "VERIFY IT IS CLOSED AND RECORD IT".
#
# `state.json` recorded radial as having the floor too, at (16,14) and (14,12),
# by a DIFFERENT mechanism than outline's: outline's header is dropped by `_fit`,
# while radial's wraps and the token lands in a row `lines[:h]` then clips.
# Re-driven on this tree, it NO LONGER REPRODUCES -- and the sizes matter, so the
# grid below reaches WIDTH 14, four columns narrower than `SIZES` starts.
#
# The first version of that sweep began at width 24 and reported radial CLEAN --
# a confident, measured, worthless zero, because the grid structurally excluded
# the two sizes the claim was about (`C-31`, input-set-as-oracle).

NARROW_SIZES = [(w, h) for w in (14, 16, 18, 20, 22, 24, 28, 34)
                for h in (10, 12, 14, 16, 20)]


async def _radial_frame(map_id: str, size):
    """The same two surfaces, with the RADIAL renderer selected."""
    app = MapperApp(WS)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        app.push_screen(MapScreen(map_id))
        await pilot.pause()
        screen = app.screen
        screen.outline_mode = False
        screen.radial_mode = True
        screen.refresh_canvas()
        await pilot.pause()

        canvas = screen.query_one("#map-canvas", Static)
        strip = screen.query_one(f"#{COUNT_REGION_ID}", Static)
        w, h = screen._canvas_size()
        painted = radial.painted_ids(screen.graph, screen._view_state(w, h))
        return {
            "canvas": _declared(canvas.render().plain),
            "strip": _declared(strip.render().plain),
            "truth": len(screen.graph.nodes) - len(painted),
        }


@pytest.mark.parametrize("map_id", ("legacy", "anidado"))
async def test_radial_agree1_holds_at_every_frame_including_the_narrow_corner(map_id):
    """RADIAL NEVER REACHES THE FLOOR, pinned so the claim cannot rot.

    This arm records an ABSENCE -- radial has no floor frame -- and an absence is
    only admissible if the probe that produced it CAN produce a non-absence
    (`C-55`'s rider). The control is the KNOWN-PRESENT case, not a fixture built
    to agree: OUTLINE, driven through the same parser over the same grid, does go
    silent, and the guard below asserts it. If outline ever stops exhibiting the
    floor here, this arm stops being evidence and says so rather than passing.
    """
    exercised = []
    for size in NARROW_SIZES:
        f = await _radial_frame(map_id, size)
        if f["truth"] <= 0:
            continue
        exercised.append(size)
        assert f["canvas"] is not None, (
            f"radial/{map_id} at {size}: the canvas is SILENT on a frame hiding "
            f"{f['truth']} node(s). Radial has acquired the floor it was measured "
            "not to have -- this is a new finding, not a stale record"
        )
        assert f["canvas"] == f["truth"] == f["strip"], (
            f"radial/{map_id} at {size}: canvas={f['canvas']} strip={f['strip']} "
            f"truth={f['truth']} -- AGREE-1 requires all three to match"
        )

    assert exercised, (
        f"radial/{map_id}: no size in the grid hid a single node, so this arm "
        "asserted nothing about agreement"
    )


@pytest.mark.parametrize("map_id", ("legacy", "anidado"))
async def test_the_narrow_grid_really_does_reach_a_floor_in_outline(map_id):
    """THE CONTROL FOR THE ARM ABOVE, and it is the load-bearing row.

    Radial's zero means something only because the same grid, the same parser and
    the same screen DO produce canvas silence for outline. Without this, a parser
    that had quietly stopped finding the token would report radial clean and
    outline clean and look like good news.
    """
    silent = []
    for size in NARROW_SIZES:
        f = await _frame(map_id, size)
        if f["truth"] > 0 and f["canvas"] is None:
            silent.append(size)
    assert silent, (
        f"outline/{map_id}: the canvas declared at EVERY size in the narrow grid, "
        "so this grid no longer reaches a floor and radial's clean result above "
        "is not evidence of anything"
    )
