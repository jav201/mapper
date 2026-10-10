"""Cursor navigation over a tree graph — A5a of batch
`2026-10-09-modular-batch` (LLR-MOD.1.1).

Home of `NavigationModel`, the cursor-navigation model the map screen
(and the repo screens) read.  A5a moves the model only — the nav concern
(cursor actions, `_repoint`, crumb, open-ficha/home/back) lands here at
B8.  The name is re-exported from `mapper.app` so historical
`from mapper.app import NavigationModel` sites keep resolving
(LLR-MOD.3.1); `screens/*` modules import it here directly once the
sibling screens move (the B-02 remediation, LLR-MOD.6.1: no `screens`
-> `app` back-edge).
"""
from __future__ import annotations

from typing import TYPE_CHECKING
from mapper.screens.common import map_hint
from mapper.widgets.chrome import HintLine

if TYPE_CHECKING:
    from mapper.model import Graph


class NavigationModel:
    """Cursor navigation over a tree graph."""

    def __init__(self, graph: Graph):
        self.graph = graph
        self.cursor = graph.root_id

    def children(self, nid: str | None = None) -> list[str]:
        nid = nid or self.cursor
        return self.graph.children_of(nid) if nid else []

    def parent(self) -> str | None:
        return self.graph.parent_of(self.cursor) if self.cursor else None

    def next_sibling(self) -> str | None:
        p = self.parent()
        if p is None:
            return None
        sibs = self.children(p)
        if self.cursor not in sibs:
            return None
        idx = sibs.index(self.cursor)
        return sibs[idx + 1] if idx + 1 < len(sibs) else None

    def prev_sibling(self) -> str | None:
        p = self.parent()
        if p is None:
            return None
        sibs = self.children(p)
        if self.cursor not in sibs:
            return None
        idx = sibs.index(self.cursor)
        return sibs[idx - 1] if idx > 0 else None

    def first_child(self) -> str | None:
        ch = self.children()
        return ch[0] if ch else None


class NavOps:
    """MapScreen's `nav` concern (moved verbatim at 2026-10-09-modular-batch Spine B).

    A plain mixin composed into `MapScreen` (screen.py): it declares no BINDINGS, no
    DEFAULT_CSS and no `@on` handlers (Textual ignores them on a non-DOMNode base), and its
    method names are disjoint from every other concern's (LLR-MOD.2.1, LLR-MOD.2.2).
    """

    def _current_crumb(self) -> list[str]:
        prefix = self.source_crumb or [self.map_id]
        if self.source_crumb:
            prefix = prefix + [f"linked: {self.map_id}"]
        return prefix

    def _repoint(self, target: str | None) -> None:
        """Move the cursor to *target* once the guard answered (PDR C2)."""
        if target not in self.graph.nodes:
            target = self.graph.root_id
        self.nav.cursor = target
        self.refresh_canvas()

    def action_next_sibling(self) -> None:
        nxt = self.nav.next_sibling()
        if nxt:
            self.nav.cursor = nxt
            self.refresh_canvas()

    def action_prev_sibling(self) -> None:
        prv = self.nav.prev_sibling()
        if prv:
            self.nav.cursor = prv
            self.refresh_canvas()

    def action_child(self) -> None:
        ch = self.nav.first_child()
        if ch:
            self.nav.cursor = ch
            self.refresh_canvas()

    def action_parent(self) -> None:
        p = self.nav.parent()
        if p:
            self.nav.cursor = p
            self.refresh_canvas()

    def action_home(self) -> None:
        self._guard_draft(self.app.pop_screen)

    def action_back_or_home(self) -> None:
        """`esc` clears a live search; with none live it leaves the map (`#D38`).

        The hint line promises `esc limpiar` the moment a search is submitted,
        and before this branch existed `escape` popped the screen
        UNCONDITIONALLY -- so an operator who followed the hint left the map.
        Painting a hint for behaviour nobody implemented is the defect `AT-052`
        exists for, one surface over.

        The seat's label stays `volver` and the branch lives here, which `#D10`
        requires: a chord whose LABEL changes with state breaks the whole-seat
        pin's static set equality, and the pin is what makes "help shows exactly
        the keys that work here" checkable at all.

        The two identical arms this replaced -- `if self.source_crumb: pop else:
        pop` -- are gone.  A branch whose sides are the same statement reads as a
        distinction the code does not make.

        The guard is `_search_is_live`, shared with the hint line.

        IT CLEARS IN EVERY REGIME (`LLR-N07.3.4`, `#D43`), which reverses what
        `Inc-4b` shipped.  There the shared predicate read the RESOLUTION, so
        above the renderer's bound this handler popped the screen on the first
        press while it cleared below it -- one chord, two meanings, selected by
        how big the map happened to be.  The count region declares the query at
        every size now, so there is something to clear at every size, and the
        chord means one thing.  A second `esc`, with no query live, still leaves.
        """
        if self._search_is_live():
            self.query_text = ""
            self.refresh_canvas()
            self.query_one(HintLine).set_hint(map_hint())
            return
        self._guard_draft(self.app.pop_screen)
