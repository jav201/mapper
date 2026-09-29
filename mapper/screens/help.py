"""The legend: the keys that work on the active screen, and the glyphs its view paints.

US-N16 «leyenda».  `?` explains THIS view -- its keys (`HLR-N16.1`), its glyph
vocabulary drawn in the view's own styles (`HLR-N16.2`), and the keys that work
inside the legend itself (`HLR-N16.4`).
"""
from __future__ import annotations

from itertools import groupby

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static

from mapper import darkside
from mapper.keymap import SCOPE_APP, SCOPE_HELP, bindings_for, textual_bindings

# `LLR-N16.2.3`'s row-length clause: every painted row of the scrolling body is
# exactly this many cells -- `#help-dialog`'s width 80, less its 2+2 padding and
# the 1-cell scrollbar.  A row wider than the pane would wrap, and the wrapped
# half would read as a row of its own.
LEGEND_ROW_CELLS = 75
_KEY_CELLS = 10
_SAMPLE_CELLS = 12
_INDENT = "  "

# `A-104` -- ASSUMPTION, queued for the operator: a compound row (one `01b` row
# naming several styles, e.g. `V19`) paints ALL its samples on ONE line, each
# in its own style, under ONE caption.  `False` paints one line per member,
# repeating the caption.  No arm depends on this: they assert over painted
# (glyph, style) pairs, not over lines.
COMPOUND_ON_ONE_LINE = True

# `01b` §3.6, verbatim.
SECTION_KEYS = "teclas de esta vista"
SECTION_VOCABULARY = "vocabulario de esta vista"
SECTION_COLOURS = "colores con empleo"
FOOTER_LINES = ("cada vista tiene SU leyenda — ", "misma tecla, contenido de la vista")


def _cells(s: str) -> int:
    return Text(s).cell_len


def _trimmed(text: Text) -> Text:
    """Drop the last row's newline, which would paint an empty row under it."""
    if text.plain.endswith("\n"):
        text.right_crop(1)
    return text


def vocabulary_for(view: str) -> list[tuple[str, str, str, str]]:
    """`LLR-N16.2.1`: the members `view`'s legend paints, in declaration order,
    read from the ONE declaration -- never a copy of it."""
    wanted = set(darkside.LEGEND_VIEWS.get(view, ()))
    return [m for m in darkside.DECLARED_VOCABULARY if m[0] in wanted]


class HelpScreen(ModalScreen[None]):
    """Modal legend for one scope and one view.

    Help is scoped, not global: showing a key that does nothing here is the
    discoverability bug this batch exists to remove (US-N03).
    """

    # Its own scope.  Borrowing the palette's meant binding `enter -> run_selected`,
    # a method this screen does not define, which was a silent no-op.
    BINDINGS = [
        Binding(key, action, label, priority=priority)
        for key, action, label, priority in textual_bindings(SCOPE_HELP)
    ]

    CSS = """
    HelpScreen {
        align: center middle;
        background: #000000 70%;
    }
    #help-dialog {
        width: 80;
        height: 90%;
        max-height: 28;
        background: #121212;
        padding: 1 2;
    }
    /* S-08 (LLR-R05.1).  The map scope carries 27 bindings in 5 groups, which the
       body renders as 40 rows — more than `max-height` shows at any terminal
       size.  Before this rule the surplus was clipped away with no way to reach
       it, and the whole 11-member `view` group fell off the bottom in silence.
       The BINDINGS scroll while the title does not: the title is the one row
       that tells the operator which view they are reading. */
    #help-bindings {
        height: 1fr;
        overflow-y: auto;
        scrollbar-size-vertical: 1;
    }
    #help-title {
        margin-bottom: 1;
    }
    """

    def __init__(self, scope: str = SCOPE_APP, view: str | None = None) -> None:
        super().__init__()
        self.scope = scope
        # HLR-N16.2: the title names the VIEW; a screen that declares none is
        # named by its scope.
        self.view = view or scope

    def compose(self) -> ComposeResult:
        body = [Static(self._render_keymap(), id="help-content")]
        vocabulary = vocabulary_for(self.view)
        # LLR-N16.2.2: an empty vocabulary omits its section -- and the colour
        # rows, which exist to explain the vocabulary's hues.
        if vocabulary:
            body.append(Static(self._render_vocabulary(vocabulary), id="help-vocabulary"))
            body.append(Static(self._render_colours(), id="help-colours"))
        body.append(Static(self._render_footer(), id="help-footer"))
        yield Vertical(
            Static(self._render_title(), id="help-title"),
            VerticalScroll(*body, id="help-bindings"),
            id="help-dialog",
        )

    # -- painting ----------------------------------------------------------
    # LLR-N16.2.3: every string reaches the surface through `darkside.fit`,
    # which coerces with `darkside.plain` and bounds the row in cells.  Nothing
    # here is handed to a markup-parsing sink: `Text.assemble` of `(str, style)`
    # pairs parses none, which is why the title is a `Text` and not a `str`.

    def _render_title(self) -> Text:
        close = next(b for b in bindings_for(SCOPE_HELP) if b.action == "dismiss_none")
        hint = f"{close.glyph} {close.label}"
        title = darkside.fit(f"leyenda · {self.view}", LEGEND_ROW_CELLS - _cells(hint)).rstrip()
        gap = LEGEND_ROW_CELLS - _cells(title) - _cells(hint)
        return Text.assemble(
            (title, f"bold {darkside.INK}"),
            (" " * gap, ""),
            (darkside.fit(close.glyph, _cells(close.glyph)), darkside.ACCENT),
            (" " + darkside.fit(close.label, _cells(close.label)), darkside.ASH),
        )

    def _render_keymap(self) -> Text:
        label_cells = LEGEND_ROW_CELLS - len(_INDENT) - _KEY_CELLS
        parts: list[tuple[str, str]] = [(SECTION_KEYS + "\n", f"bold {darkside.ASH}")]
        entries = bindings_for(self.scope)
        for group, bindings in groupby(
            sorted(entries, key=lambda b: b.group), key=lambda b: b.group
        ):
            parts.append((f"\n{darkside.fit(group, LEGEND_ROW_CELLS).rstrip()}\n", darkside.ASH))
            for binding in bindings:
                parts.append((_INDENT, ""))
                parts.append((darkside.fit(binding.glyph, _KEY_CELLS), darkside.ACCENT))
                parts.append((darkside.fit(binding.label, label_cells) + "\n", darkside.INK))
        return _trimmed(Text.assemble(*parts))

    def _render_vocabulary(self, members: list[tuple[str, str, str, str]]) -> Text:
        """LLR-N16.2.1 / HLR-N16.2: each sample painted in its declared style."""
        text = Text.assemble((f"\n{SECTION_VOCABULARY}\n\n", f"bold {darkside.ASH}"))
        rows = groupby(members, key=lambda m: m[0])
        for _row_id, group in rows:
            group = list(group)
            lines = [group] if COMPOUND_ON_ONE_LINE else [[m] for m in group]
            for line in lines:
                self._vocabulary_line(text, line)
        return _trimmed(text)

    def _vocabulary_line(self, text: Text, members: list[tuple[str, str, str, str]]) -> None:
        samples: list[tuple[str, str]] = []
        for _row_id, glyph, _label, style in members:
            if glyph:
                if samples:
                    samples.append((" ", ""))
                shown = darkside.fit(glyph, min(_cells(glyph), LEGEND_ROW_CELLS - len(_INDENT)))
                samples.append((shown, darkside.resolve_style(style)))
        width = sum(_cells(s) for s, _ in samples)
        label = members[0][2]
        label_cells = LEGEND_ROW_CELLS - len(_INDENT) - _SAMPLE_CELLS
        text.append(_INDENT)
        for sample, style in samples:
            text.append(sample, style=style)
        if width >= _SAMPLE_CELLS:
            # A sample wider than its column keeps its own line rather than
            # being cut: a truncated glyph misdescribes the form it stands for.
            text.append(" " * (LEGEND_ROW_CELLS - len(_INDENT) - width) + "\n")
            text.append(_INDENT + " " * _SAMPLE_CELLS)
        else:
            text.append(" " * (_SAMPLE_CELLS - width))
        text.append(darkside.fit(label, label_cells) + "\n", style=darkside.INK)

    def _render_colours(self) -> Text:
        label_cells = LEGEND_ROW_CELLS - len(_INDENT) - 3
        parts: list[tuple[str, str]] = [(f"\n{SECTION_COLOURS}\n\n", f"bold {darkside.ASH}")]
        for swatch, label, token in darkside.DECLARED_COLOURS:
            parts.append((_INDENT, ""))
            parts.append((darkside.fit(swatch, 1), darkside.resolve_style(token)))
            parts.append(("  ", ""))
            parts.append((darkside.fit(label, label_cells) + "\n", darkside.INK))
        return _trimmed(Text.assemble(*parts))

    def _render_footer(self) -> Text:
        return Text.assemble(
            ("\n" + "\n".join(darkside.fit(line, LEGEND_ROW_CELLS) for line in FOOTER_LINES),
             darkside.ASH)
        )

    # -- actions -----------------------------------------------------------
    # HLR-N16.4: the legend's own keys.  They act on the pane whether or not it
    # holds focus, so the seat rows are true in every focus state.

    def _pane(self) -> VerticalScroll:
        return self.query_one("#help-bindings", VerticalScroll)

    def action_legend_up(self) -> None:
        self._pane().scroll_up(animate=False)

    def action_legend_down(self) -> None:
        self._pane().scroll_down(animate=False)

    def action_legend_page_up(self) -> None:
        self._pane().scroll_page_up(animate=False)

    def action_legend_page_down(self) -> None:
        self._pane().scroll_page_down(animate=False)

    def action_legend_home(self) -> None:
        self._pane().scroll_home(animate=False)

    def action_legend_end(self) -> None:
        self._pane().scroll_end(animate=False)

    def action_dismiss_none(self) -> None:
        self.dismiss(None)
