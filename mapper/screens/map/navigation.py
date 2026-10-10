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
