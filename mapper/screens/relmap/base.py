"""The relation screen's shared painters and the frozen host↔renderer surface.

The surface this module defines is D1 of `PDR-2026-10-25-relmap-r2-batch`,
frozen at the R2 PDR so lanes 3/4/5 (matrix/gaps/sheet) draft against names
that do not move.  Amended at the trunk Inc-2 review pass (orchestrator
ruling, `LED-2026-10-25-r2.18`): `row_count(state) -> int` joins the
renderer protocol and the vestigial `lens` field drops from `ViewState`.

* `ViewState` — the focused state ONE renderer receives: the derived
  `RelMap` (``None`` in the unavailable state), the host's fixed refusal
  ``notice``, the host-owned ``focus`` node selection, the ``cursor`` row,
  the host-supplied ranked ``gaps`` rows, and the viewport ``(width,
  height)``.  ``cursor`` is the ACTIVE view's row index on that view's OWN
  row axis — the host keeps one cursor per view and moves it within
  ``[0, row_count(state))``, clamped at the ends, never wrapping.
* ``RelMapView.paint(state) -> list[Text]`` — the ONE paint entry a
  renderer exposes.  Renderers never import each other; this state is their
  only crossing.  A landed renderer's obligation: when ``state.notice`` is
  set (the unavailable state), the fixed refusal line IS the body — paint
  it through the same one sink and no body content beside it.
* ``RelMapView.row_count(state) -> int`` — the rows the host's cursor may
  address in THIS view for this state, on the view's own axis: the
  ranked-gap rows for gaps, the node list for matrix/sheet.  0 means the
  cursor has nothing to move over; the placeholder always answers 0.
* ``RelMapView.toggle(kind: str) -> str`` — the one toggle-state channel
  (COND-ARCH-1).  The kind vocabulary is ``enter`` (matrix lens — the
  state word is ``panel lens``, the prototype crumb), ``c`` (sheet chain
  density — the words ``direct only`` / ``stacked chain`` per LLR-RVS.3.3)
  and ``k`` (gaps by-kind grouping — the word ``by kind``); each kind owns
  state in the RENDERER of its home view, the entry flips it and returns
  the state word for the host's crumb slot, ``""`` when *kind* is not this
  renderer's.  The host stores the word PER VIEW: the crumb shows the
  active view's own word, never another view's, and switching back
  restores it.  The host's ``action_*`` call the ACTIVE renderer's entry
  and repaint — one mechanism, the same for all three lanes.
* ``build_view(name)`` — the wiring convention: renderer module
  ``mapper/screens/relmap/<name>.py`` exposes ``build_view() -> RelMapView``.
  Until a lane lands its module the host paints ``PendingView``, the honest
  placeholder, so the chrome the host owns (crumb, keybar, notice) is
  exercisable from this increment on.

The ONE label sink is `label` below: every host- or renderer-assembled label
that carries descriptor- or canon-derived text passes through
``darkside._row_text``/``fit`` (``plain`` + LF/TAB/CR → single space,
``mapper/darkside.py:576-621``) into explicit-style ``Text``
(COND-SEC-1, LLR-RVH.5.2) — never a markup-parsing sink, and the width cut
applies to the COERCED string, never the reverse (the C-10 order).
"""
from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Protocol, Sequence

from rich.text import Text

from mapper import darkside
from mapper.relmap.gaps import Gap
from mapper.relmap.model import RelMap

#: The three views, in seat order (`1`/`2`/`3`).
VIEW_NAMES = ("matrix", "gaps", "sheet")


def label(value: object, width: int, style: str = "") -> Text:
    """*value* as ONE markup-safe row of at most *width* cells.

    The seam is ``darkside._row_text``/``fit``: the coercion (``plain`` plus
    LF/TAB/CR as single spaces) runs BEFORE the width cut, and the result is an
    explicit-style ``Text`` — markup in a descriptor name or canon title
    renders literally, and a payload cannot forge a second row.
    """
    text = Text(darkside.fit("" if value is None else str(value), width))
    if style:
        text.stylize(style)
    return text


def frame(rows: Sequence[Text]) -> Text:
    """The renderer's row list as one ``Text`` for a ``Static.update`` — the
    join the host uses so a renderer returns rows and never touches a widget."""
    out = Text()
    for i, row in enumerate(rows):
        if i:
            out.append("\n")
        out.append_text(row)
    return out


@dataclass(frozen=True)
class ViewState:
    """The focused state ONE renderer receives — the frozen D1 surface.

    ``cursor`` is the active view's row index on that view's own row axis;
    the host keeps one cursor per view, clamped within
    ``[0, row_count(state))`` (see the protocol below) — never wrapping.
    """

    relmap: RelMap | None
    notice: str | None
    focus: str | None
    cursor: int
    gaps: tuple[Gap, ...]
    width: int
    height: int


class RelMapView(Protocol):
    """The one paint entry, the row-count query and the one toggle-state
    channel per renderer."""

    name: str

    def paint(self, state: ViewState) -> list[Text]:
        """Paint the viewport ``(state.width, state.height)`` as rows.

        The renderer's notice obligation: when ``state.notice`` is set (the
        unavailable state) the fixed refusal line IS the body — painted
        through the one ``label`` sink, with no body content beside it.
        """
        ...

    def row_count(self, state: ViewState) -> int:
        """The rows the host's cursor may address in THIS view for *state* —
        the view's own axis (ranked-gap rows for gaps, the node list for
        matrix/sheet).  0 means the cursor has nothing to move over."""
        ...

    def toggle(self, kind: str) -> str:
        """Flip *kind* state, returning the state word for the host's crumb."""
        ...


class PendingView:
    """The pre-lane renderer: honest about what it is not.

    Paints the fixed refusal ``notice`` when there is one, else the view's
    name and the node's focus — the chrome-shaped minimum that keeps the
    host's canvas real.  Owns no toggle state, so both toggles return ``""``
    (the seat's out-of-view inertness is the whole behaviour here), and its
    row axis is empty — ``row_count`` answers 0, so the cursor keys are
    honest no-ops on a pre-lane view.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    def paint(self, state: ViewState) -> list[Text]:
        rows: list[Text] = []
        if state.notice:
            rows.append(label(state.notice, state.width))
        elif state.relmap is not None:
            rows.append(label(f"{self.name} · {state.focus or 'no map'}", state.width))
        for y in range(len(rows), state.height):
            rows.append(label("", state.width))
        return rows

    def toggle(self, kind: str) -> str:
        return ""

    def row_count(self, state: ViewState) -> int:
        return 0


def build_view(name: str) -> RelMapView:
    """The renderer for *name* — live module when its lane has landed, else
    ``PendingView``.

    A renderer module exposes ``build_view() -> RelMapView`` (the wiring
    convention frozen in this module's docstring).  Only the module being
    ABSENT falls back: an import error inside a landed renderer module is a
    real defect and propagates, never silently degrades to the placeholder.
    """
    if name not in VIEW_NAMES:
        raise ValueError(f"unknown relmap view: {name!r}")
    module_name = f"mapper.screens.relmap.{name}"
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        if exc.name != module_name:
            raise
        return PendingView(name)
    return module.build_view()
