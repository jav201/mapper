"""Small motion helpers for the darkside UI.

These are intentionally decoupled from screens so the same 300 ms in_out_cubic
breath can be applied wherever the cursor/selection moves.
"""
from __future__ import annotations

from textual.widgets import Static


def pulse_cursor(widget: Static) -> None:
    """A quick 300 ms breath on a static canvas when the cursor moves.

    Call this after updating the rendered text in a selection-driven Static
    (e.g. ``#repo-canvas`` or ``#map-canvas``). It does not change the render
    itself; it just softens the visual snap of a cursor change.
    """

    def _restore() -> None:
        widget.styles.animate("opacity", 1.0, duration=0.15, easing="in_out_cubic")

    widget.styles.animate("opacity", 0.75, duration=0.15, easing="in_out_cubic", on_complete=_restore)
