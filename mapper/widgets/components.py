"""Darkside interaction components (Static-based renderers).

Each component renders three states: default / focused / disabled.  Focus is the
solid blue block; disabled sinks to STEP.  Blue is reserved for interactivity.
"""
from __future__ import annotations

from textual.message import Message
from textual.widgets import Static

from mapper import darkside

_ON_ACCENT = f"bold {darkside.GROUND} on {darkside.ACCENT}"


class _DsBase(Static):
    """Base for focus-aware darkside components."""

    can_focus = True

    def __init__(self, *, disabled: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self._disabled = disabled

    @property
    def disabled(self) -> bool:
        return self._disabled

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self._disabled = value
        self.can_focus = not value
        self.refresh()

    def on_focus(self) -> None:
        self.refresh()

    def on_blur(self) -> None:
        self.refresh()

    def _state(self) -> str:
        if self.disabled:
            return "disabled"
        if self.has_focus:
            return "focused"
        return "default"


# ---------------------------------------------------------------------------
# 1. Switch — word flip; the active word wears the blue block
# ---------------------------------------------------------------------------
class DsSwitch(_DsBase):
    """Binary switch rendered as on/off word pair."""

    class Changed(Message):
        """Emitted when the switch value changes."""

        def __init__(self, value: bool) -> None:
            super().__init__()
            self.value = value

    def __init__(self, value: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.value = value

    def render(self):
        state = self._state()
        if state == "disabled":
            return darkside.Text.assemble(
                (" on ", darkside.WORDMARK), (" ", ""), (" off ", darkside.WORDMARK)
            )
        on_style = _ON_ACCENT if self.value else f"{darkside.MUT} on {darkside.STEP}"
        off_style = _ON_ACCENT if not self.value else f"{darkside.MUT} on {darkside.STEP}"
        edge = ("▐", darkside.ACCENT) if state == "focused" else (" ", "")
        return darkside.Text.assemble(edge, (" on ", on_style), (" ", ""), (" off ", off_style))

    def action_activate(self) -> None:
        if self.disabled:
            return
        self.value = not self.value
        self.post_message(self.Changed(self.value))
        self.refresh()

    def on_key(self, event) -> None:
        if event.key in {"space", "enter"}:
            event.stop()
            self.action_activate()

    def on_click(self) -> None:
        self.action_activate()


# ---------------------------------------------------------------------------
# 2. Stepper — - value +; the ± carry the affordance
# ---------------------------------------------------------------------------
class DsStepper(_DsBase):
    """Numeric stepper."""

    class Changed(Message):
        def __init__(self, value: int) -> None:
            super().__init__()
            self.value = value

    def __init__(self, value: int = 0, min_value: int | None = None,
                 max_value: int | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.value = value
        self.min_value = min_value
        self.max_value = max_value

    def render(self):
        state = self._state()
        if state == "disabled":
            return darkside.Text.assemble(
                ("  - ", darkside.WORDMARK),
                (f" {self.value} ", darkside.WORDMARK),
                (" + ", darkside.WORDMARK),
            )
        minus = _ON_ACCENT if state == "focused" else darkside.ACCENT
        plus = _ON_ACCENT if state == "focused" else darkside.ACCENT
        return darkside.Text.assemble(
            ("  - ", minus),
            (f" {self.value} ", darkside.INK),
            (" + ", plus),
        )

    def _change(self, delta: int) -> None:
        if self.disabled:
            return
        new = self.value + delta
        if self.min_value is not None:
            new = max(self.min_value, new)
        if self.max_value is not None:
            new = min(self.max_value, new)
        if new != self.value:
            self.value = new
            self.post_message(self.Changed(self.value))
        self.refresh()

    def action_decrement(self) -> None:
        self._change(-1)

    def action_increment(self) -> None:
        self._change(1)

    def on_key(self, event) -> None:
        if event.key in {"minus", "left"}:
            event.stop()
            self.action_decrement()
        elif event.key in {"plus", "right"}:
            event.stop()
            self.action_increment()


# ---------------------------------------------------------------------------
# 3. Slider — track STEP, fill INK, handle a blue block
# ---------------------------------------------------------------------------
class DsSlider(_DsBase):
    """Horizontal slider with 0..1 value."""

    class Changed(Message):
        def __init__(self, value: float) -> None:
            super().__init__()
            self.value = value

    def __init__(self, value: float = 0.0, width: int = 18, **kwargs) -> None:
        super().__init__(**kwargs)
        self.value = max(0.0, min(1.0, value))
        self.width = width

    def render(self):
        state = self._state()
        if state == "disabled":
            return darkside.Text("─" * self.width, style=darkside.WORDMARK)
        pos = max(0, min(self.width - 1, round(self.value * (self.width - 1))))
        parts: list[tuple[str, str]] = []
        for i in range(self.width):
            if i == pos:
                parts.append(("▮", _ON_ACCENT if state == "focused" else darkside.ACCENT))
            elif i < pos:
                parts.append(("━", darkside.INK))
            else:
                parts.append(("─", darkside.STEP))
        return darkside.Text.assemble(*parts)

    def _nudge(self, delta: float) -> None:
        if self.disabled:
            return
        self.value = max(0.0, min(1.0, self.value + delta))
        self.post_message(self.Changed(self.value))
        self.refresh()

    def action_decrement(self) -> None:
        self._nudge(-1 / max(1, self.width - 1))

    def action_increment(self) -> None:
        self._nudge(1 / max(1, self.width - 1))

    def on_key(self, event) -> None:
        if event.key in {"left", "minus"}:
            event.stop()
            self.action_decrement()
        elif event.key in {"right", "plus"}:
            event.stop()
            self.action_increment()


# ---------------------------------------------------------------------------
# 4. Segmented — active option is the blue block
# ---------------------------------------------------------------------------
class DsSegmented(_DsBase):
    """Segmented control (tab strip's little sibling)."""

    class Changed(Message):
        def __init__(self, index: int, value: str) -> None:
            super().__init__()
            self.index = index
            self.value = value

    def __init__(self, options: list[str], active: int = 0, **kwargs) -> None:
        super().__init__(**kwargs)
        self.options = options
        self.active = max(0, min(len(options) - 1, active))

    def render(self):
        state = self._state()
        parts: list[tuple[str, str]] = []
        if state == "focused":
            parts.append(("▐", darkside.ACCENT))
        for i, opt in enumerate(self.options):
            if i > 0:
                parts.append((" ", ""))
            if state == "disabled":
                parts.append((f" {opt} ", f"{darkside.STEP} on {darkside.PANEL}"))
            elif i == self.active:
                parts.append((f" {opt} ", _ON_ACCENT))
            else:
                parts.append((f" {opt} ", f"{darkside.MUT} on {darkside.STEP}"))
        return darkside.Text.assemble(*parts)

    def _move(self, delta: int) -> None:
        if self.disabled or not self.options:
            return
        self.active = (self.active + delta) % len(self.options)
        self.post_message(self.Changed(self.active, self.options[self.active]))
        self.refresh()

    def action_next(self) -> None:
        self._move(1)

    def action_previous(self) -> None:
        self._move(-1)

    def on_key(self, event) -> None:
        if event.key in {"left", "minus"}:
            event.stop()
            self.action_previous()
        elif event.key in {"right", "plus"}:
            event.stop()
            self.action_next()


# ---------------------------------------------------------------------------
# 5. Progress — contiguous ▰▱ meter
# ---------------------------------------------------------------------------
class DsProgress(Static):
    """Progress meter (read-only)."""

    can_focus = False

    def __init__(self, filled: int = 0, total: int = 5, accent_current: bool = False,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.filled = filled
        self.total = total
        self.accent_current = accent_current

    def render(self):
        return darkside.step_meter(self.filled, self.total, self.accent_current)


# ---------------------------------------------------------------------------
# 6. Spinner — braille cycle in ACCENT
# ---------------------------------------------------------------------------
class DsSpinner(Static):
    """Braille loading spinner (read-only)."""

    can_focus = False

    _FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    def __init__(self, frame: int = 0, label: str = "cargando…", disabled: bool = False,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.frame = frame
        self.label = label
        self._disabled = disabled

    @property
    def disabled(self) -> bool:
        return self._disabled

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self._disabled = value
        self.refresh()

    def render(self):
        glyph = self._FRAMES[self.frame % len(self._FRAMES)]
        if self._disabled:
            return darkside.Text.assemble(("· ", darkside.WORDMARK), (self.label, darkside.WORDMARK))
        return darkside.Text.assemble((f"{glyph} ", darkside.ACCENT), (self.label, darkside.MUT))


# ---------------------------------------------------------------------------
# 7. TextField — cursor ▌ ACCENT; placeholder STEP
# ---------------------------------------------------------------------------
class DsTextField(_DsBase):
    """Static text-field lookalike."""

    class Changed(Message):
        def __init__(self, value: str) -> None:
            super().__init__()
            self.value = value

    def __init__(self, value: str = "", placeholder: str = "nombre del mapa…",
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.value = value
        self.placeholder = placeholder

    def render(self):
        state = self._state()
        if state == "disabled":
            return darkside.Text(f" {self.value or self.placeholder} ", style=darkside.WORDMARK)
        if state == "focused":
            return darkside.Text.assemble(("▌", darkside.ACCENT), (self.value, darkside.INK))
        if self.value:
            return darkside.Text(f" {self.value} ", style=darkside.MUT)
        return darkside.Text(f" {self.placeholder} ", style=darkside.WORDMARK)


# ---------------------------------------------------------------------------
# 8. Pagination — ‹ n/m ›
# ---------------------------------------------------------------------------
class DsPagination(_DsBase):
    """Pagination control."""

    class Changed(Message):
        def __init__(self, page: int) -> None:
            super().__init__()
            self.page = page

    def __init__(self, page: int = 1, total: int = 1, **kwargs) -> None:
        super().__init__(**kwargs)
        self.page = max(1, min(total, page))
        self.total = max(1, total)

    def render(self):
        state = self._state()
        if state == "disabled":
            return darkside.Text.assemble(
                (" ‹ ", darkside.WORDMARK),
                (f"{self.page}/{self.total}", darkside.WORDMARK),
                (" › ", darkside.WORDMARK),
            )
        arrow = _ON_ACCENT if state == "focused" else darkside.ACCENT
        return darkside.Text.assemble(
            (" ‹ ", arrow),
            (f"{self.page}/{self.total}", darkside.INK),
            (" › ", arrow),
        )

    def _set(self, page: int) -> None:
        if self.disabled:
            return
        page = max(1, min(self.total, page))
        if page != self.page:
            self.page = page
            self.post_message(self.Changed(self.page))
        self.refresh()

    def action_previous(self) -> None:
        self._set(self.page - 1)

    def action_next(self) -> None:
        self._set(self.page + 1)

    def on_key(self, event) -> None:
        if event.key in {"left", "minus"}:
            event.stop()
            self.action_previous()
        elif event.key in {"right", "plus"}:
            event.stop()
            self.action_next()


# ---------------------------------------------------------------------------
# 9. Chip — tag on STEP; focused wears the blue block
# ---------------------------------------------------------------------------
class DsChip(_DsBase):
    """Tag chip."""

    class Changed(Message):
        def __init__(self, selected: bool) -> None:
            super().__init__()
            self.selected = selected

    def __init__(self, label: str, selected: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.chip_label = label
        self.selected = selected

    def render(self):
        state = self._state()
        if state == "disabled":
            return darkside.Text(f" {self.chip_label} ", style=f"{darkside.STEP} on {darkside.PANEL}")
        # Focused and selected must not render identically (LLR-N06.3).  They did:
        # one `focused or selected` branch painted both the same, so "which chip
        # does ↵ act on" was unanswerable from the screen.  Focus carries the edge
        # marker; selection carries the block.
        if state == "focused":
            return darkside.Text.assemble(
                ("▐", darkside.ACCENT),
                (f" {self.chip_label} ", _ON_ACCENT if self.selected else f"{darkside.INK} on {darkside.STEP}"),
            )
        if self.selected:
            return darkside.Text(f" {self.chip_label} ", style=_ON_ACCENT)
        return darkside.Text(f" {self.chip_label} ", style=f"{darkside.INK} on {darkside.STEP}")

    def action_activate(self) -> None:
        if self.disabled:
            return
        self.selected = not self.selected
        self.post_message(self.Changed(self.selected))
        self.refresh()

    def on_key(self, event) -> None:
        if event.key in {"space", "enter"}:
            event.stop()
            self.action_activate()

    def on_click(self) -> None:
        self.action_activate()
