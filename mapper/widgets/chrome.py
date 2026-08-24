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
    """Grouped key hint bar."""

    def __init__(self, groups: Sequence[tuple[str, Sequence[tuple[str, str]]]], **kwargs) -> None:
        super().__init__(**kwargs)
        self.groups = list(groups)
        self.update(darkside.keybar(self.groups))

    def set_groups(self, groups: Sequence[tuple[str, Sequence[tuple[str, str]]]]) -> None:
        self.groups = list(groups)
        self.update(darkside.keybar(self.groups))


class HintLine(Static):
    """Single-line next-step hint."""

    def __init__(self, text: str, key: str | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
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
