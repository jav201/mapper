"""Chrome widgets built on the darkside design system."""
from __future__ import annotations

from typing import Sequence

from textual.containers import Container
from textual.dom import NoActiveAppError
from textual.widgets import Static

from mapper import darkside


class TabStrip(Static):
    """Top tab strip with optional breadcrumb."""

    def __init__(self, active: str, crumb: list[str] | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.active = active
        self.crumb = crumb
        self.update(darkside.tab_strip(active, crumb))

    def on_resize(self) -> None:
        self.update(darkside.tab_strip(self.active, self.crumb, width=self.size.width))

    def set_crumb(self, crumb: list[str] | None) -> None:
        self.crumb = crumb
        self.update(darkside.tab_strip(self.active, crumb, width=self.size.width))


# Last-resort width when neither the widget nor the app can be measured yet.
# It is the batch's declared context of use, and it is a FALLBACK -- reaching it
# used to be the NORMAL case, which is the defect described below.
#
# SPELLED TWICE: `darkside._crumb_line` hardcodes the same 118 as its own
# zero-width fallback.  Two modules now carry the declared context independently
# and nothing makes them agree.  De-duplicating it is a structural change and is
# carried to `Inc-REPAIR`, not smuggled in here.
_KEYBAR_FALLBACK_CELLS = 118


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
        """The widget's own width, then the app's, then the declared context.

        The app's width is the useful middle rung: during `compose` this widget
        has no size yet but the terminal does, so the first render can be RIGHT
        rather than merely correctable.
        """
        if self.size.width:
            return self.size.width
        try:
            return self.app.size.width or _KEYBAR_FALLBACK_CELLS
        except NoActiveAppError:
            # THE ONLY EXPECTED FAILURE, named rather than swallowed: `self.app`
            # raises this when the widget is constructed outside a running app.
            # A bare `except Exception` would silently restore the 118-cell
            # render this class exists to stop producing, for ANY reason at all
            # -- including one introduced later by something unrelated.
            return _KEYBAR_FALLBACK_CELLS

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
