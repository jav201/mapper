"""Chrome widgets built on the darkside design system."""
from __future__ import annotations

from typing import Sequence

from textual.containers import Container
from textual.dom import NoActiveAppError
from textual.widgets import Static

from mapper import darkside


def _resolved_width(widget) -> int:
    """The widget's own width, then the app's, then the declared context.

    ONE LADDER, because it is a POLICY and a policy spelled twice drifts exactly
    as a number does. `TabStrip` and `KeyBar` carried verbatim copies until
    `Inc-REPAIR` S-A, and the cost was the next rung: add a fourth step to one
    and the other silently keeps three. The alias `_KEYBAR_FALLBACK_CELLS` went
    with them -- it named the wrong widget once `TabStrip` became half its use
    sites, and nothing referenced it but prose.

    THE APP RUNG IS THE USEFUL ONE. During `compose` a widget has no size yet but
    the terminal does, so the first render can be RIGHT rather than merely
    correctable -- which matters because a later `update()` replaces the CONTENT
    and does not re-run the height the layout already latched.
    """
    if widget.size.width:
        return widget.size.width
    try:
        return widget.app.size.width or darkside.DECLARED_CONTEXT_CELLS
    except NoActiveAppError:
        # THE ONLY EXPECTED FAILURE, named rather than swallowed: `widget.app`
        # raises this when the widget is constructed outside a running app. A
        # bare `except Exception` would silently restore the fallback render
        # this function exists to stop producing, for ANY reason at all.
        return darkside.DECLARED_CONTEXT_CELLS


class TabStrip(Static):
    """Top tab strip with optional breadcrumb, rendered at its MEASURED width.

    THE SAME LADDER `KeyBar` GOT AT `Inc-CRUMB`, and this widget is why that one
    was found: bounding the crumb shortened `TabStrip` and removed the reflow
    that had been correcting `KeyBar` by accident. The sibling was fixed then and
    this one was carried as `SEC-F1` until `Inc-REPAIR` S-A.

    Without it, `__init__` called `tab_strip` with no width, `tab_strip` passed
    that to `_crumb_line`, and `_crumb_line` took its own fallback. Measured
    before the fix: the constructor passed NO WIDTH AT ALL, so `_crumb_line`
    rendered 97 cells regardless of the terminal -- identical at 30, 40 and 60
    because the terminal was never consulted. The number is right and the first
    framing of it was not: three equal readings of one width-independent value
    is a tautology of the call site, not three measurements converging, and
    reading it as evidence points at `_crumb_line` when the defect was at the
    call site. Post-fix the three widths genuinely differ: 29 / 35 / 35.

    NOT LIVE, and the reason is the point: the content was superseded before
    paint and the height clamped by `max-height: 3`. THE CSS LID WAS
    LOAD-BEARING -- a lid over content not bounded in Python, the exact shape
    `Inc-CRUMB` was opened to stop shipping.
    """

    def __init__(self, active: str, crumb: list[str] | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.active = active
        self.crumb = crumb
        self.update(darkside.tab_strip(active, crumb, width=self._width()))

    def _width(self) -> int:
        return _resolved_width(self)

    def on_mount(self) -> None:
        # Belt to `on_resize`'s braces, as `KeyBar` carries: by mount the widget
        # usually has its real size, and this render does not depend on a size
        # CHANGE ever happening.
        self.update(darkside.tab_strip(self.active, self.crumb, width=self._width()))

    def on_resize(self) -> None:
        self.update(darkside.tab_strip(self.active, self.crumb, width=self._width()))

    def set_crumb(self, crumb: list[str] | None) -> None:
        self.crumb = crumb
        self.update(darkside.tab_strip(self.active, crumb, width=self._width()))


class KeyBar(Static):
    """Grouped key hint bar that renders at its MEASURED width.

    THE FIRST RENDER USED TO IGNORE THAT, and this docstring has claimed
    otherwise ever since the hard-coded 118 was "removed": `__init__` called
    `darkside.keybar(self.groups)` with NO width, taking the 118 default, and
    only `on_resize` corrected it.

    WHAT SURVIVES THE CORRECTION IS THE HEIGHT, NOT THE CONTENT -- and the first
    version of this docstring got that backwards, saying no corrective resize
    fires and that "the 118-cell render stands".  Both are refuted by
    measurement: the resize DOES fire, `keybar` IS called again with the true
    width, and the pre-fix widget ends up HOLDING the corrected render.  At 35
    columns the pre-fix and fixed widgets paint identical text.  What differs is
    the region -- FOUR rows against ONE -- because auto-height was computed from
    the 118-cell render when layout ran, and a later `update()` does not re-run
    that calculation.

    So the rule is not "make sure a resize fires"; one does.  It is that a widget
    must never be LAID OUT from a render it is about to replace.  Three rows of a
    fourteen-row frame were taken from `#map-canvas` by a widget whose painted
    text was already correct.

    `Inc-CRUMB` did not introduce this; it removed the mask.  Bounding the crumb
    shortened `TabStrip` from three rows to two, and that reflow had been firing
    the corrective resize by accident.

    The width is resolved at CONSTRUCTION and again at mount, with the resize
    re-render kept as the UPDATE path rather than the correction path.
    """

    def __init__(self, groups: Sequence[tuple[str, Sequence[tuple[str, str]]]], **kwargs) -> None:
        super().__init__(**kwargs)
        self.groups = list(groups)
        self.update(darkside.keybar(self.groups, width=self._width()))

    def _width(self) -> int:
        return _resolved_width(self)

    def set_groups(self, groups: Sequence[tuple[str, Sequence[tuple[str, str]]]]) -> None:
        self.groups = list(groups)
        self.update(darkside.keybar(self.groups, width=self._width()))

    def on_mount(self) -> None:
        # The belt to `on_resize`'s braces: by mount the widget usually has its
        # real size, and this render does not depend on a size CHANGE ever
        # happening.  It is what makes the FIRST painted frame right rather than
        # the second.
        self.update(darkside.keybar(self.groups, width=self._width()))

    def on_resize(self) -> None:
        self.update(darkside.keybar(self.groups, width=self._width()))


class HintLine(Static):
    """Single-line next-step hint."""

    def __init__(self, text: str, key: str | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.text = text
        self.key = key
        self.update(darkside.hint_line(text, key))

    def set_hint(self, text: str, key: str | None = None) -> None:
        """Replace the hint after mount.

        Named to match its siblings `TabStrip.set_crumb` and `KeyBar.set_groups`.
        Without it the hint was fixed at construction, so it could not say what
        the operator's next step actually is — which is the whole point of a hint.
        """
        self.text = text
        self.key = key
        self.update(darkside.hint_line(text, key))


class GroupBox(Container):
    """Container with darkside panel background depth.

    The app stylesheet should set `.group-box { background: #121212; }`.
    """

    def __init__(self, *children, **kwargs) -> None:
        super().__init__(*children, **kwargs)
        self.add_class("group-box")
