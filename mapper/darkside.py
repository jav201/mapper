"""Darkside design-system primitives (rich only, no Textual dependency).

Every colour token carries EXACTLY ONE job.  A hue with two jobs cannot be
adjudicated by the census in `tests/test_darkside.py`, and it licenses painting
two different things identically -- which is the whole failure the census
exists to catch.  The jobs, one sentence each:

  GROUND    the page behind everything.
  PANEL     a raised surface sitting on GROUND.
  STEP      a divider or an inert track on a surface.
  INK       readable body text.
  ASH       segundo escalon legible: the middle rung of the text ramp on the
            black ground, one step below INK, where STEP and WORDMARK are too
            dark to be read as text at all.
  MUT       secondary or dimmed text, and absent information.
  WORDMARK  the quietest mark on the page; present but not to be read.
  ACCENT    interactivity ONLY -- "donde puedes actuar".  Never a label.
  WARN      outstanding attention: work is pending, due, or at risk, and
            nothing has failed.
  ALERT     failure or blockage: this item cannot proceed as it stands.
  PULSE     trabajo en curso: this item is being worked on right now, and
            nothing is pending, overdue, at risk, or failed.
  SAGE      completitud / vigente.
  TEAL      procedencia repo.
  VIOLET    relaciones / enlaces.

WARN's job deliberately does NOT read "or in flight".  Work the machine is
doing and work the operator owes demand opposite things -- patience versus
action -- so one token spanning both has a job that cannot be scanned, and a
census over it cannot tell the two apart.  PULSE owns "in progress"; WARN owns
the obligation.  Narrowing WARN is what keeps `sites classifying as both == 0`
satisfiable at all.
"""
from __future__ import annotations

import re
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
ASH = "#a3a3a3"
MUT = "#737373"
ACCENT = "#1783ff"
WARN = "#ffd230"
ALERT = "#ff4f42"
PULSE = "#ff9ecb"
WORDMARK = "#3a3a3a"

# Paleta v2 -- three hues with declared jobs, so a later batch cannot quietly
# reuse one for a second meaning.  Blue stays interactivity-only and severity
# stays WARN/ALERT; these three carry meanings neither of those families owns.
SAGE = "#2fbf71"
TEAL = "#22b8cf"
VIOLET = "#9775fa"

_TOKEN_VALUE = re.compile(r"^#[0-9a-fA-F]{6}$")

# The tokens that are a SURFACE to paint on rather than a mark to paint with.
# Declared, because "semantic token pairs" has to be decidable before the
# contrast floor can quantify over it -- and the two classes separate by a wide
# measured margin: surfaces top out at WORDMARK, semantics start at MUT, with a
# 4x luminance gap and nothing in between.  The PAIRS stay derived; only the
# four-name class boundary is written down.
SURFACES = frozenset({GROUND, PANEL, STEP, WORDMARK})


def tokens() -> dict[str, str]:
    """Every declared colour token, name -> value, DERIVED from this module.

    Derived rather than listed because a hand-written set is an unproven claim:
    a token added above would be invisible to the hue census, to `Canvas`'s
    tone guard and to the contrast floor, each of which reads this one function.
    """
    return {
        name: value
        for name, value in globals().items()
        if not name.startswith("_")
        and name.isupper()
        and isinstance(value, str)
        and _TOKEN_VALUE.match(value)
    }


def tone_set() -> frozenset[str]:
    """The declared token values, for consumers that validate a tone."""
    return frozenset(tokens().values())


def semantic_tokens() -> dict[str, str]:
    """The tokens that carry a meaning, as opposed to the surfaces beneath them.

    The contrast floor quantifies over these pairs; including the surfaces
    drops it to the GROUND/PANEL distance, which measures the page and not the
    palette.
    """
    return {n: v for n, v in tokens().items() if v not in SURFACES}

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
        # THE TERMINAL'S WIDTH, NOT `target_width`.  `target_width` is the TAB
        # ROW's natural width -- `max(width, tabs + wordmark)`, floor 62 -- so
        # handing it to the crumb gives the crumb a budget LARGER THAN THE
        # FRAME below 62 columns.  The line was then cell-correct against 62 and
        # wrapped anyway: measured at 30 columns it wanted six rows and the lid
        # ate it entirely, and between 35 and 60 the visible line ended
        # mid-title with neither ellipsis nor `+N`, because `fit`'s ellipsis sat
        # in the clipped row.  That is the "lie by omission" the declaration
        # below exists to prevent, reintroduced by passing the wrong variable.
        return Text.assemble(line, "\n", _crumb_line(crumb, width))

    return line


# The ONE place the fallback BUDGET is written -- the batch's declared context
# of use, in cells.
#
# It was spelled THREE times: `_crumb_line`'s zero-width fallback below,
# `keybar`'s default parameter, and `chrome._KEYBAR_FALLBACK_CELLS`. The carry
# that named the defect recorded TWO of the three; the third surfaced only when
# the arm pinning it was written.
#
# NARROWLY CLAIMED, because "the one place 118 is written" would be false: the
# suite spells the declared terminal SIZE `(118, 34)` in a dozen places, and
# `app.py`/`rail.py` document a 118-column auto-hide threshold that is
# `MIN_CANVAS_WIDTH + RAIL_WIDTH + INSPECTOR_WIDTH` -- a DERIVED number that
# collides with this one by arithmetic accident. Folding those together would be
# drift, not tidiness.
#
# It is a FALLBACK. Reaching it means neither the widget nor the app could be
# measured, which inside a running app is a defect rather than a condition.
DECLARED_CONTEXT_CELLS = 118


# The crumb's chrome: the ` / ` between parts, and the ` +N … ` that declares how
# many ancestors were dropped.  Reserved so the budget can never be spent so
# completely that the declaration itself has nowhere to go.
_CRUMB_SEP_CELLS = 3
_CRUMB_DROP_CELLS = 8
# Below this there is no room to say anything useful about WHERE YOU ARE, so the
# tail is shown alone and the ancestors are declared.  `keybar` makes the same
# call in the same words: the affordance outranks the context.
_CRUMB_TAIL_MIN_CELLS = 12


def _cells(s: str) -> int:
    """Display cells, not characters -- the unit the layout is actually in.

    A `len()` here would under-count every wide glyph and over-count every
    combining mark, which is how a cell budget written in characters stops
    bounding anything.  The same measure `fit` truncates against.
    """
    return Text(s).cell_len


def _crumb_line(crumb: list[str], width: int) -> Text:
    """The breadcrumb, BOUNDED IN CELLS and truncated VISIBLY.

    THE PARTS ARE FILE-DERIVED AND WERE UNBOUNDED, which made this a fourth
    unbounded strip on the map screen.  `tab_strip`'s `width` reached only the
    wordmark spacer above and never this line, so one long ficha title decided
    the whole layout: measured at 4000 characters, `TabStrip` rendered 54 rows at
    80x24 and pushed both `#map-canvas` and the search count region OFF-VIEWPORT
    -- the same collapse `Inc-STRIPS` bounded on two other strips, reached
    through a different vector.  Degradation starts long before the extreme: 500
    characters already costs a third of the canvas at 80x24.

    THE TAIL IS THE PART WORTH KEEPING.  It is the node the cursor is on and it
    is painted `INK`; the ancestors are context in `MUT`.  So the budget is spent
    from the RIGHT -- the tail first, then as many ancestors as still fit -- and
    whatever is dropped is DECLARED rather than elided.  `keybar` states the
    reason in its own docstring: a bare ellipsis "is a lie by omission: it says
    something was cut but not that anything is missing, let alone how much".
    """
    if not crumb:
        return Text("")
    budget = width if width > 0 else DECLARED_CONTEXT_CELLS

    tail = crumb[-1]
    tail_budget = max(_CRUMB_TAIL_MIN_CELLS, budget - _CRUMB_DROP_CELLS)
    tail_text = fit(tail, min(tail_budget, _cells(tail))).rstrip()

    kept: list[str] = []
    used = _cells(tail_text)
    for part in reversed(crumb[:-1]):
        shown = fit(part, min(budget, _cells(part))).rstrip()
        cost = _cells(shown) + _CRUMB_SEP_CELLS
        if used + cost + _CRUMB_DROP_CELLS > budget:
            break
        kept.append(shown)
        used += cost
    kept.reverse()

    dropped = len(crumb) - 1 - len(kept)
    rendered: list[tuple[str, str]] = []
    if dropped > 0:
        # DECLARED, not elided: the count says how much of the path is missing.
        rendered.append((f"+{dropped} ", INK))
        rendered.append(("… / ", MUT))
    # NOT `escape(...)`, and this is a correction rather than a simplification.
    # `escape` adds a cell per markup-shaped bracket run AFTER the budget has
    # been spent, so the rendered line could exceed a budget that was measured
    # honestly: a `[b]`-bearing title breached the lid at SEVENTY of seventy
    # widths from 20 to 89 -- including both widths this module's closing arm
    # drives, which pass only because their fixture titles are letter runs.
    #
    # It was also wrong on its own terms.  `Text.assemble` with `(str, style)`
    # tuples appends LITERAL text and parses no markup, so the backslash was
    # painted on screen rather than protecting anything.  NO COERCION IS LOST:
    # `MapScreen` applies `plain` to every part before it arrives here, and
    # `fit` applies it again above.
    for part in kept:
        rendered.append((part, MUT))
        rendered.append((" / ", MUT))
    rendered.append((tail_text, INK))
    return Text.assemble(*rendered)


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
def keybar(
    groups: Sequence[tuple[str, Sequence[tuple[str, str]]]],
    width: int = DECLARED_CONTEXT_CELLS,
    help_key: str = "?",
) -> Text:
    """Render grouped key hints for the footer, truncating VISIBLY.

    group names in STEP, key glyphs in ACCENT, labels in MUT.

    When the bar does not fit, a bare `…` is a lie by omission: it says something
    was cut but not that anything is missing, let alone how much or how to see it.
    This ends with `… +N  ? todas`, naming the count hidden and the key that shows
    them.  Measured before this change: the bar rendered 216 cells at a hard-coded
    118, so 9 of 17 bindings were shown and `m cobertura` — the entry point to the
    coverage flow — was simply invisible.
    """
    def _binding_parts(key: str, label: str, first: bool) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        if not first:
            out.append(("  ", ""))
        out.append((key, ACCENT))
        out.append((f" {label}", MUT))
        return out

    total = sum(len(bindings) for _, bindings in groups)
    parts: list[tuple[str, str]] = []
    for gi, (group_name, bindings) in enumerate(groups):
        if gi > 0:
            parts.append(("   ", ""))
        parts.append((f"{group_name} ", f"{STEP}"))
        for bi, (key, label) in enumerate(bindings):
            parts.extend(_binding_parts(key, label, bi == 0))

    text = Text.assemble(*parts)
    if text.cell_len <= width:
        return text

    # Re-assemble, counting how many bindings actually fit inside the budget the
    # marker leaves behind.
    marker_width = len(f" … +{total}  {help_key} todas")
    budget = max(0, width - marker_width)
    kept: list[tuple[str, str]] = []
    shown = 0
    running = Text()
    for gi, (group_name, bindings) in enumerate(groups):
        head: list[tuple[str, str]] = []
        if gi > 0:
            head.append(("   ", ""))
        head.append((f"{group_name} ", f"{STEP}"))
        for bi, (key, label) in enumerate(bindings):
            candidate = head + _binding_parts(key, label, bi == 0)
            probe = Text.assemble(*(kept + candidate))
            if probe.cell_len > budget:
                head = []
                break
            kept.extend(candidate)
            head = []
            shown += 1
            running = probe

    hidden = total - shown
    out = Text.assemble(*kept)
    out.append(f" … +{hidden}", style=WORDMARK)
    out.append(f"  {help_key}", style=ACCENT)
    out.append(" todas", style=MUT)
    return out


# Hint line ----------------------------------------------------------------
def hint_line(text: str, key: str | None = None) -> Text:
    """Render a next-step hint line."""
    parts: list[tuple[str, str]] = [("siguiente ▸ ", MUT), (plain(text), MUT)]
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
    # `name` and `note` are file- OR REMOTE-derived: the repo screen feeds this
    # a git branch name and a commit subject/author, so the input author is
    # anyone who has landed a commit in a repository the operator opens.  Coerce
    # here rather than at the call site, so the next caller cannot forget --
    # `hint_line` and `fit` already work this way.
    name, note = plain(name), plain(note)
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
# Control characters other than tab and newline are replaced, not escaped: a
# terminal acts on them.  An ANSI cursor-move or an OSC-52 clipboard write inside
# a ficha title reaches the compositor verbatim, and markup escaping does nothing
# about either — measured, see 01-requirements.md §Amendment 2 S-B2.
#
# THE single list of code points that may not reach a painted surface.  Declared
# once, here: `_CONTROL_MAP` is derived from it and every threshold and every
# test reads it rather than restating it, because two copies of a list like this
# agree on the day they are written and drift the first time one is edited.
#
# PRESERVED, each with its reason: TAB and LF are the only two code points in
# the classes below that the layout depends on.
PRESERVED_CODE_POINTS = frozenset({0x0009, 0x000A})

# The list is exactly Unicode's Cc (control), Cf (format), Zl (line separator)
# and Zp (paragraph separator) classes, MINUS PRESERVED_CODE_POINTS.  It is
# spelled out as literal ranges so a reviewer can read it, and
# `tests/test_darkside_census.py` re-derives it from `unicodedata` and asserts
# equality.  That derivation is the point: an oracle built FROM this list can
# never detect that the list is short, and twice it was.
#
# Hand-picking produced both near-misses.  A row labelled "C0 except TAB and LF"
# also omitted U+000D; a row labelled "zero-width and invisible" stopped one
# code point short of U+2061..U+2064.  The U+E0020..U+E007F TAG block is why it
# matters most: those points render as nothing everywhere, map 1:1 onto ASCII,
# and reach an exported SVG as a payload the operator cannot see and any later
# reader recovers trivially.
#
# Ranges are inclusive on both ends.  Every entry is written as a number, never
# as the character itself, so this file contains no control byte.
COERCION_RANGES: tuple[tuple[int, int], ...] = (
    (0x0000, 0x0008), (0x000B, 0x001F),       # C0 except TAB and LF
    (0x007F, 0x009F),                         # DEL and C1
    (0x00AD, 0x00AD),                         # soft hyphen
    (0x0600, 0x0605), (0x06DD, 0x06DD),       # Arabic number/sign format controls
    (0x061C, 0x061C),                         # Arabic letter mark
    (0x070F, 0x070F),                         # Syriac abbreviation mark
    (0x0890, 0x0891), (0x08E2, 0x08E2),       # Arabic number signs
    (0x180E, 0x180E),                         # Mongolian vowel separator
    (0x200B, 0x200F),                         # zero-width, and the bidi marks
    (0x2028, 0x202E),                         # line/para seps, bidi embed/override
    (0x2060, 0x2064),                         # word joiner, invisible operators
    (0x2066, 0x206F),                         # bidi isolates, deprecated controls
    (0xFEFF, 0xFEFF),                         # byte-order mark
    (0xFFF9, 0xFFFB),                         # interlinear annotation
    (0x110BD, 0x110BD), (0x110CD, 0x110CD),   # Kaithi number signs
    (0x13430, 0x1343F),                       # Egyptian hieroglyph format controls
    (0x1BCA0, 0x1BCA3),                       # shorthand format controls
    (0x1D173, 0x1D17A),                       # musical symbol beams and slurs
    (0xE0001, 0xE0001), (0xE0020, 0xE007F),   # language tag, and the TAG block
)

_CONTROL_MAP = {
    cp: "�"
    for lo, hi in COERCION_RANGES
    for cp in range(lo, hi + 1)
}


def plain(value: object) -> str:
    """Coerce any file-derived value into a string that is safe to render.

    The single coercion helper every renderer of sidecar text must pass through.
    It deliberately does NOT call `rich.markup.escape`: these strings are placed
    into `Text` objects with explicit styles, and `Text` does not parse markup, so
    escaping there is a no-op that merely prints visible backslashes.  Safety from
    markup comes from never handing a file-derived `str` to a markup-parsing sink.
    """
    if not isinstance(value, str):
        value = "" if value is None else str(value)
    return value.translate(_CONTROL_MAP)


# `INC8-SEC-F1`.  `plain()` deliberately PRESERVES tab and newline
# (`PRESERVED_CODE_POINTS`) for a caller that wants a real multi-line field --
# `widgets/inspector.py` hands a notes field through `plain` into a widget that
# is allowed to wrap onto several rows. `fit` has no such caller: every result
# becomes exactly ONE row of a fixed-width panel, so a label carrying a literal
# LF painted a REAL line break once the padded string reached a `Text` sink,
# fabricating a row the row-length budget never accounted for; a literal TAB
# reaches a real terminal as its OWN cursor motion, past whatever padding was
# computed here. Each becomes a single space, keeping the cell count `plain`
# already measured. `\r` is listed for the same reason though `plain` already
# coerces it (it sits in `COERCION_RANGES`): a row-bounding function should not
# depend on that staying true elsewhere to keep its own single-row promise.
_ROW_BREAKERS = {0x0009: " ", 0x000A: " ", 0x000D: " "}


def fit(s: str, w: int) -> str:
    """Pad or truncate *s* to exactly *w* display cells, as ONE row.

    `INC8-C1-F1`.  `w <= 0` is handled BEFORE reaching `Text.truncate`: Rich's
    own `set_cell_size`, for a single-cell-width string, truncates via a plain
    Python slice (`text[:max_width]`) rather than special-casing a
    non-positive width -- so `truncate(0, overflow="ellipsis")` sliced with
    `[: -1]`, dropping the LAST character and keeping every other one, then
    appended the ellipsis on top. Measured: `fit("leyenda · atlas", 0)`
    returned a **15-cell** string, not an empty one, discovered while clamping
    `screens/help.py::_render_title` against an oversized seat label
    (`INC8-SEC-F3`). A budget of zero or fewer cells can only ever mean "".
    """
    if w <= 0:
        return ""
    s = plain(s).translate(_ROW_BREAKERS)
    text = Text(s)
    if text.cell_len > w:
        text.truncate(w, overflow="ellipsis")
        return text.plain
    return text.plain + " " * (w - text.cell_len)


# ---------------------------------------------------------------------------
# `LLR-N16.2.1` — THE GLYPH VOCABULARY, DECLARED ONCE.
#
# CREATED HERE BY `Inc-7` RATHER THAN BY `Inc-8`, per cut amendment `A-101`.
# `LLR-N13.1.5`'s `PRED-VIS` requires the damaged-map card glyph to be A MEMBER
# OF THIS DECLARATION, asserted at run time -- and a clause cannot depend on a
# declaration the NEXT increment creates.  `Inc-8`'s legend CONSUMES this; it
# does not build a second one.
#
#: `LLR-N16.2.1` -- the glyph vocabulary, DECLARED ONCE and DERIVED, never
#: transcribed.  Each member is a 4-TUPLE `(row id, glyph, label, style
#: token)`, exactly as `01b-ux-decisions.md` DECISION 3 sections 3.1-3.4 spells
#: it.  THE SOURCE OF TRUTH IS `01b`; nothing here may be edited without the
#: row in `01b` moving first.
#:
#: THE STYLE IS A TOKEN NAME, NOT A RESOLVED HEX.  `01b` declares tokens and the
#: legend must paint what the renderer paints, so the comparison has to be on
#: the same representation; `resolve_style` turns it into paint at the sink.
#:
#: THE GLYPH IS THE LEGEND'S SAMPLE, DERIVED FROM `01b`'s GLYPH CELL BY A
#: WRITTEN RULE (`INC7-CR-R2-F2`) -- stated once, in
#: `tests/test_vocabulary_declaration.py::sample_by_style`, and applied to every
#: row there.  An EMPTY glyph means the cell is PROSE and the rule cannot
#: derive a sample from it (`V4b`, `V12`): an open question for the operator,
#: never a guess.
#:
#: `tests/test_vocabulary_declaration.py` asserts SET EQUALITY between this
#: tuple and the members it derives from `01b` (`INC7-CR-R2-F3`): dropping a
#: row, renaming its id, or drifting its glyph, label or style reddens.
#:
#: Compound rows contribute ONE MEMBER PER DISTINCT TRIPLE (`A-103`); rows that
#: name the same painted FORM collapse onto the first id that names it (`V4a`
#: into `V4`, `01b` Amendment 2(b)); a `DEFERRED(#D7)` row contributes nothing
#: (`V18`, Amendment 2(a)).

#: `01b` row `V22`'s glyph, as its own constant so the pending `⊘`/`⦸` verdict
#: is a one-line swap (Amendment 1).
DAMAGED_MAP_GLYPH = "\u2298"

DECLARED_VOCABULARY: tuple[tuple[str, str, str, str], ...] = (
    ('V1', " rrhh ", 'rama abierta', 'INK on PANEL'),
    ('V2', " nómina ", 'coincidencia de búsqueda', 'bold GROUND on WARN'),
    ('V3', "▸ inv +23", 'rama plegada (23 dentro)', 'MUT on PANEL'),
    ('V4', "∙ ∙ ∙", 'territorio sin explorar', 'WORDMARK'),
    ('V5', "▔▔▔▔", 'nodo seleccionado', 'ACCENT'),
    ('V6', "┌─┐", 'minimapa: tu ventana en el todo', 'ACCENT'),
    ('V4b', "", 'enlace entre nodos', 'MUT'),
    ('V4b', "", 'enlace entre nodos', 'ACCENT'),
    ('V7', "plegadas: inventarios · ventas — 41 nodos", 'overflow declaration; the `N` **shall** reconcile with the sum of the `+N` in every painted pill', 'WORDMARK'),
    ('V8', "minimapa · 128 nodos", 'minimap caption; `N` = total nodes in the graph', 'WORDMARK'),
    ('V9', "┌──┐ │ │ └──┘", 'viewport — the part of the territory now on screen', 'ACCENT on PANEL'),
    ('V10', "▓ ▒ ░", 'territory density', 'WORDMARK on PANEL'),
    ('V11', "▐", 'coincide con la lente', 'WARN on PANEL'),
    ('V12', "", 'fuera de la lente', 'WORDMARK'),
    ('V13', "╎", 'enlace atenuado', 'STEP'),
    ('V14', "ficha completa ✓", 'sin campos pendientes', 'SAGE on PANEL'),
    ('V15', "faltan campos ░", 'ficha incompleta', 'MUT on PANEL'),
    ('V16', "∗", 'lente de campos', 'ACCENT'),
    ('V17', "⇄ enlazado", 'enlaza mapas', 'VIOLET on PANEL'),
    ('V19', "█", 'coverage microbar', 'SAGE'),
    ('V19', "█", 'coverage microbar', 'INK'),
    ('V19', "░", 'coverage microbar', 'WORDMARK'),
    ('V20', "▲ vence", 'actas vencidas', 'WARN on PANEL'),
    ('V21', "∙", 'lit `= nodo con acta`, unlit `= sin acta`', 'MUT on PANEL'),
    ('V21', "∙", 'lit `= nodo con acta`, unlit `= sin acta`', 'WORDMARK on PANEL'),
    ('V22', DAMAGED_MAP_GLYPH, 'mapa dañado — no se pudo leer', 'INK on PANEL'),
)

#: `01b` Amendment 2(b): a glyph may be a SET of codepoints.  A member listed
#: here also owns every codepoint in each inclusive range -- `V4`'s scattered
#: braille, written in `V4a`'s cell as `U+2800`-`U+28FF`.  DECLARED, CHECKED
#: AGAINST 01B: this dict is written by hand, and
#: `tests/test_vocabulary_declaration.py::test_amendment_2b_V4a_collapses_into_V4_carrying_its_braille_range`
#: pins it equal to what the document derives -- it is not itself computed
#: from `01b` at import time.
DECLARED_GLYPH_RANGES: dict[str, tuple[tuple[int, int], ...]] = {
    "V4": ((0x2800, 0x28FF),),
}

#: `HLR-N16.2` -- which members each view's legend paints, by row id.
#: DECLARED, CHECKED AGAINST 01B: written by hand from the `01b` SECTION a row
#: sits in (`3.1`/`3.2` the atlas canvas, `3.4` the sala), and
#: `tests/test_vocabulary_declaration.py::test_hlr_n16_2_each_view_paints_the_rows_of_its_own_01b_sections`
#: pins it equal to what the document derives.  `3.3` (lens) belongs to no
#: view: US-N14 is deferred whole (`#D23`).  A view absent here has an empty
#: vocabulary (`LLR-N16.2.2`).
LEGEND_VIEWS: dict[str, tuple[str, ...]] = {
    "atlas": ("V1", "V2", "V3", "V4", "V5", "V6", "V4b", "V7", "V8", "V9", "V10"),
    "sala": ("V17", "V19", "V20", "V21", "V22"),
}

#: `LLR-N16.2.1`'s SECOND derived set: `01b` §3.5's colours with a job, as
#: `(swatch, label, token)`.  Not members of the vocabulary above.
DECLARED_COLOURS: tuple[tuple[str, str, str], ...] = (
    ("█", "azul — donde puedes actuar", "ACCENT"),
    ("█", "ámbar — atención / vence", "WARN"),
    ("█", "sage — completo / vigente", "SAGE"),
    ("█", "teal — vino del repo", "TEAL"),
    ("█", "violeta — enlaza mapas", "VIOLET"),
)


def _declared_modifiers() -> frozenset[str]:
    """The non-token words `01b`'s own style cells actually use (`bold`, `on`).

    Derived from `DECLARED_VOCABULARY` and `DECLARED_COLOURS` -- the two
    corpora `resolve_style` exists to paint -- rather than hand-listed, so a
    modifier this batch never declares cannot quietly become allow-listed.
    """
    names = tokens()
    words: set[str] = set()
    for _vid, _glyph, _label, style in DECLARED_VOCABULARY:
        words.update(w for w in style.split() if w not in names)
    for _swatch, _label, token in DECLARED_COLOURS:
        words.update(w for w in token.split() if w not in names)
    return frozenset(words)


def resolve_style(declared: str) -> str:
    """`LLR-N16.2.1`: a declared style (`"bold GROUND on WARN"`) as paint
    (`"bold #000000 on #ffd230"`).

    Only whole words that name a darkside token, or a modifier `01b` actually
    declares (`bold`, `on`), pass through. Everything else RAISES.

    `declared` becomes part of a Rich *style* string, not painted text -- so an
    unknown word was never "visible" the way the previous docstring claimed.
    Handed unexamined to `Style.parse` at the paint sink, `link file:///x`
    painted a live OSC-8 hyperlink and `[bold]` raised inside the render call
    instead of at this boundary. Raising HERE, at the one seam every declared
    style must cross, turns both into a defect this function catches rather
    than one the paint sink discovers.
    """
    names = tokens()
    modifiers = _declared_modifiers()
    out = []
    for word in declared.split():
        if word in names:
            out.append(names[word])
        elif word in modifiers:
            out.append(word)
        else:
            raise ValueError(f"resolve_style: undeclared style word {word!r} in {declared!r}")
    return " ".join(out)

#: `LLR-N13.1.5`'s DECLARED CARD STATE -- the Spanish string that ships.
#: The `\u21b5` is load-bearing: `#D28` escalates this seat from `MUT` to `INK`
#: BECAUSE the copy invites an ACTION, so a card without the invitation would
#: take the escalated style while deleting the reason for it.
DAMAGED_MAP_STATE = "mapa da\u00f1ado \u2014 \u21b5 ver por qu\u00e9"

#: THE PENDING-PROJECTION LIST IS GONE, and its removal is the point: the
#: compound-row projection was RULED (`A-103`), so `V19` and `V21` are no
#: longer a declared absence -- they are members, one per distinct triple, and
#: `V4b` (which that list never named) is too.  A list of known gaps is only
#: honest while the gap is open; kept past its ruling it becomes a second,
#: stale opinion about a question that has been answered.
