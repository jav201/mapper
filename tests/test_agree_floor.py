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
from mapper.views import outline

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
