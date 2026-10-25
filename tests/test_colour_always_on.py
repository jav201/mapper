"""Q1 — colour always on: ``NO_COLOR`` cannot desaturate the painted screen.

HLR-Q1.1 / LLR-Q1.1.1 (mechanism decided by orchestrator ruling R3; no
``--no-color`` opt-out per operator ruling Q5).  Mutant M-Q1-1 — deleting the
neutralisation in ``MapperApp.__init__`` — turns every node here RED.

Textual's ``App.__init__`` pops ``NO_COLOR`` from the process environment and
appends a ``Monochrome`` line filter when it was set, so every test controls
the variable deliberately: the harness shell may export it, and it is this
module's input, not ambient noise.
"""
from __future__ import annotations

import os

import pytest
from textual.filter import Monochrome

from mapper.app import MapperApp
from tests.test_repair_layout import WIDE_SIZES, _open_map, _tree

SIZE = WIDE_SIZES[0]


def _painted_frame(screen) -> bytes:
    """The composited frame serialized as (text, style) runs — the bytes the
    operator sees, styles included.  Textual's ``Monochrome`` line filter
    rewrites the style runs of the strips this compositor hands out, so a
    desaturated frame serializes to different bytes."""
    rows = [
        [(seg.text, str(seg.style)) for seg in strip]
        for strip in screen._compositor.render_strips()  # noqa: SLF001
    ]
    return repr(rows).encode("utf-8")


@pytest.mark.parametrize("value", ["1", "", "an arbitrary value"])
def test_no_color_removed_before_super(tmp_path, monkeypatch, value):
    """LLR-Q1.1.1 layer-0 arm: construction with ``NO_COLOR`` SET (review
    inc002-F1 parametrizes the declared boundary catalog — set / set-empty /
    arbitrary value; the pop is value-independent, and the set-empty regime was
    declared but had no arm) removes the variable from the process environment
    before the Textual base constructor runs, so no ``Monochrome`` filter can
    be installed."""
    monkeypatch.setenv("NO_COLOR", value)
    app = MapperApp(tmp_path)
    assert "NO_COLOR" not in os.environ
    assert not any(isinstance(f, Monochrome) for f in app._filters), (
        "a Monochrome line filter is active — NO_COLOR leaked into the app"
    )


async def test_painted_screen_byte_identical_with_and_without_no_color(tmp_path, monkeypatch):
    """AT-108 black-box arm: the painted screen is byte-identical whether the
    environment carries ``NO_COLOR=1`` or not — the deliverable, not the
    mechanism.  Two real apps driven through ``run_test``: one constructed
    with the variable set, one with it absent."""
    frames = {}
    for label, present in (("set", True), ("absent", False)):
        monkeypatch.delenv("NO_COLOR", raising=False)
        if present:
            monkeypatch.setenv("NO_COLOR", "1")
        app = MapperApp(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await _open_map(app, pilot, _tree(app))
            await pilot.pause()
            # `motion.pulse_cursor` breathes the canvas opacity for 300 ms on
            # every repaint; capture only after the animation has settled, so
            # the frame is the settled screen, not a mid-breath sample.
            await pilot.wait_for_scheduled_animations()
            frames[label] = _painted_frame(app.screen)
    assert frames["set"] == frames["absent"], (
        "NO_COLOR=1 changed the painted screen — colour policy leaked to the environment"
    )
