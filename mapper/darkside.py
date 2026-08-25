"""Darkside design-system primitives (rich only, no Textual dependency)."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Sequence

from rich.markup import escape
from rich.panel import Panel
from rich.text import Text

# Palette ------------------------------------------------------------------
GROUND = "#000000"
PANEL = "#121212"
STEP = "#262626"
INK = "#f5f5f5"
MUT = "#737373"
ACCENT = "#1783ff"
WARN = "#ffd230"
ALERT = "#ff4f42"
WORDMARK = "#3a3a3a"

# Moon doodle --------------------------------------------------------------
_SYNODIC = 29.530588853
_NEW_MOON_2000 = date(2000, 1, 6)


def moon(d: date) -> tuple[str, str]:
    """Return (glyph, phase_name) for the given date."""
    days = (d - _NEW_MOON_2000).days
    age = days % _SYNODIC
    phase = age / _SYNODIC  # 0..1, 0=new, 0.5=full

    if phase < 0.0625 or phase >= 0.9375:
        return ("○", "new")
    if phase < 0.1875:
        return ("◔", "waxing crescent")
    if phase < 0.3125:
        return ("◑", "first quarter")
    if phase < 0.4375:
        return ("◕", "waxing gibbous")
    if phase < 0.5625:
        return ("●", "full")
    if phase < 0.6875:
        return ("◕", "waning gibbous")
    if phase < 0.8125:
        return ("◑", "last quarter")
    return ("◔", "waning crescent")


# Tab strip ----------------------------------------------------------------
def tab_strip(active: str, crumb: list[str] | None = None, width: int = 0) -> Text:
    """Render the darkside tab strip."""
    tabs: list[tuple[str, str]] = [
        ("c", "consultar"),
        ("p", "repo"),
        ("n", "construir"),
        ("f", "fábrica"),
    ]
    pieces: list[tuple[str, str]] = []
    for key, label in tabs:
        if key == active:
            pieces.append((f" {key} {label} ", f"bold {GROUND} on {ACCENT}"))
        else:
            pieces.append((f" {key} {label} ", f"{MUT} on {STEP}"))
        pieces.append(("  ", ""))
    # Drop trailing two spaces.
    if pieces:
        pieces.pop()

    # Right-side moon + wordmark.
    glyph, _ = moon(date.today())
    wordmark = f" {glyph} mapper"
    # Use the available width to push the wordmark to the right.
    left_text = Text.assemble(*pieces)
    target_width = max(width, left_text.cell_len + len(wordmark) + 2)
    spacer_width = max(1, target_width - left_text.cell_len - len(wordmark))
    pieces.append((" " * spacer_width, ""))
    pieces.append((wordmark, f"{WORDMARK}"))

    line = Text.assemble(*pieces)

    if crumb:
        rendered: list[tuple[str, str]] = []
        for i, part in enumerate(crumb):
            if i > 0:
                rendered.append((" / ", MUT))
            style = INK if i == len(crumb) - 1 else MUT
            rendered.append((escape(part), style))
        return Text.assemble(line, "\n", Text.assemble(*rendered))

    return line


# Group box ----------------------------------------------------------------
def group_box(renderable, pad_x: int = 1) -> Panel:
    """Invisible-bordered panel at panel depth."""
    return Panel(
        renderable,
        border_style=PANEL,
        style=f"on {PANEL}",
        padding=(0, pad_x),
    )


# Keybar -------------------------------------------------------------------
def keybar(groups: Sequence[tuple[str, Sequence[tuple[str, str]]]], width: int = 118) -> Text:
    """Render grouped key hints for the footer.

    group names in STEP, key glyphs in ACCENT, labels in MUT.
    """
    parts: list[tuple[str, str]] = []
    for gi, (group_name, bindings) in enumerate(groups):
        if gi > 0:
            parts.append(("   ", ""))
        parts.append((f"{group_name} ", f"{STEP}"))
        for bi, (key, label) in enumerate(bindings):
            if bi > 0:
                parts.append(("  ", ""))
            parts.append((key, ACCENT))
            parts.append((f" {label}", MUT))
    text = Text.assemble(*parts)
    text.truncate(width, overflow="ellipsis")
    return text


# Hint line ----------------------------------------------------------------
def hint_line(text: str, key: str | None = None) -> Text:
    """Render a next-step hint line."""
    parts: list[tuple[str, str]] = [("siguiente ▸ ", MUT), (escape(text), MUT)]
    if key:
        parts.append((f" {key}", INK))
    return Text.assemble(*parts)


# Step meter ---------------------------------------------------------------
def step_meter(filled: int, total: int, accent_current: bool = False) -> Text:
    """Render a step-meter as contiguous blocks."""
    if total <= 0:
        return Text("")
    parts: list[tuple[str, str]] = []
    for i in range(total):
        if i < filled:
            parts.append(("▰", INK))
        elif accent_current and i == filled:
            parts.append(("▱", INK))
        else:
            parts.append(("▱", STEP))
    return Text.assemble(*parts)


# Kind chip ----------------------------------------------------------------
def kind_chip(kind: str) -> Text:
    """Render a node-kind badge."""
    return Text.assemble((f" {escape(kind)} ", f"{INK} on {STEP}"))


# Drawn type (hero numbers) ------------------------------------------------
_DIGITS = {
    "0": ("███", "█ █", "█ █", "█ █", "███"),
    "1": (" █ ", "██ ", " █ ", " █ ", "███"),
    "2": ("███", "  █", "███", "█  ", "███"),
    "3": ("███", "  █", " ██", "  █", "███"),
    "4": ("█ █", "█ █", "███", "  █", "  █"),
    "5": ("███", "█  ", "███", "  █", "███"),
    "6": ("███", "█  ", "███", "█ █", "███"),
    "7": ("███", "  █", " █ ", " █ ", " █ "),
    "8": ("███", "█ █", "███", "█ █", "███"),
    "9": ("███", "█ █", "███", "  █", "███"),
}


def draw_number(s: str, style: str = INK) -> Text:
    """Render *s* as 3x5 block digits."""
    rows = [Text() for _ in range(5)]
    for ch in s:
        glyph = _DIGITS.get(ch)
        if glyph is None:
            continue
        for i, row in enumerate(glyph):
            rows[i].append(row + " ", style=style)
    return Text.assemble(*sum(([r, "\n"] for r in rows), [])[:-1])


def microbar(count: int, total: int, width: int = 10, fill: str = INK) -> Text:
    """Inline distribution bar: present never paints absent.

    Track uses WORDMARK because STEP is invisible on GROUND.
    """
    if total <= 0 or count <= 0:
        filled = 0
    else:
        filled = max(1, round(count / total * width))
    return Text.assemble(("█" * filled, fill), ("░" * (width - filled), WORDMARK))


def time_row(name: str, age_days: int, glyph: str, style: str, note: str,
             width: int = 48) -> Text:
    """One event on a shared *width*-day axis with a today rule.

    The today rule ``╎`` sits in the same rightmost column on every row.
    """
    cells = [" "] * (width + 1)
    cells[width] = "╎"
    col = max(0, width - 1 - round(age_days / 30 * (width - 2)))
    cells[col] = glyph
    parts: list[tuple[str, str]] = [(f"{name:<14}", MUT)]
    for c in cells:
        if c == "╎":
            parts.append((c, WORDMARK))
        elif c == glyph:
            parts.append((c, style))
        else:
            parts.append((c, ""))
    parts.append(("  ", ""))
    parts.append((note, MUT))
    return Text.assemble(*parts)


# Text helpers -------------------------------------------------------------
def fit(s: str, w: int) -> str:
    """Pad or truncate *s* to exactly *w* display cells."""
    s = escape(s)
    text = Text(s)
    if text.cell_len > w:
        text.truncate(w, overflow="ellipsis")
        return text.plain
    return text.plain + " " * (w - text.cell_len)
