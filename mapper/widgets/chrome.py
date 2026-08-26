"""Chrome widgets built on the darkside design system."""
from __future__ import annotations

from typing import Sequence

from textual.containers import Container
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


class KeyBar(Static):
    """Grouped key hint bar that renders at its MEASURED width.

    It previously rendered at a hard-coded 118 cells regardless of the terminal,
    so on a narrower screen it silently over-ran and on a wider one it wasted
    space.  Either way the operator could not tell which bindings were hidden.
    """

    def __init__(self, groups: Sequence[tuple[str, Sequence[tuple[str, str]]]], **kwargs) -> None:
        super().__init__(**kwargs)
        self.groups = list(groups)
        self.update(darkside.keybar(self.groups))

    def _width(self) -> int:
        return self.size.width or 118

    def set_groups(self, groups: Sequence[tuple[str, Sequence[tuple[str, str]]]]) -> None:
        self.groups = list(groups)
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
