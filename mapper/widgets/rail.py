"""The left rail — a collapsible outline of the map with coverage at a glance.

Computes its own tree from the `Graph` rather than reusing `OutlineRenderer`:
that renderer returns a `Text`, i.e. a picture, and a collapsible tree with
per-branch counts is a structure.  No `**kwargs` extracts structure back out of a
rendered `Text`, and extending `IRenderer.render` is a frozen-interface change
this batch may not make.  `widgets -> model` is allowed precisely so the rail can
walk the graph itself.
"""
from __future__ import annotations

from textual.message import Message
from textual.widgets import Static

from mapper import darkside
from mapper.model import Graph

RAIL_WIDTH = 24


class OutlineRail(Static):
    """Outline tree + per-branch missing counts + a coverage lattice."""

    can_focus = True

    class NodeSelected(Message):
        def __init__(self, node_id: str) -> None:
            super().__init__()
            self.node_id = node_id

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.graph = Graph()
        self.cursor: str | None = None
        self.collapsed: set[str] = set()

    def show(self, graph: Graph, cursor: str | None) -> None:
        self.graph = graph
        self.cursor = cursor
        self.refresh()

    def toggle(self, node_id: str | None) -> None:
        """Collapse or expand a branch."""
        if node_id is None:
            return
        if node_id in self.collapsed:
            self.collapsed.discard(node_id)
        else:
            self.collapsed.add(node_id)
        self.refresh()

    # -- structure ---------------------------------------------------------
    def visible_rows(self) -> list[tuple[str, int]]:
        """`(node_id, depth)` for every row the rail currently shows."""
        rows: list[tuple[str, int]] = []
        if self.graph.root_id is None:
            return rows

        def walk(nid: str, depth: int) -> None:
            rows.append((nid, depth))
            if nid in self.collapsed:
                return
            for child in self.graph.children_of(nid):
                walk(child, depth + 1)

        walk(self.graph.root_id, 0)
        return rows

    def subtree_missing(self, node_id: str) -> int:
        """How many required fields are unfilled in this branch, including itself.

        Consumes `Ficha.missing_required` — the model owns that definition, so the
        rail and the coverage worklist cannot disagree about what is complete.
        """
        total = 0
        stack = [node_id]
        seen: set[str] = set()
        while stack:
            nid = stack.pop()
            if nid in seen or nid not in self.graph.nodes:
                continue
            seen.add(nid)
            total += len(self.graph.nodes[nid].ficha.missing_required(self.graph.schema))
            stack.extend(self.graph.children_of(nid))
        return total

    # -- rendering ---------------------------------------------------------
    def render(self):
        if self.graph.root_id is None:
            return darkside.Text.assemble(("  (mapa vacío)", darkside.MUT))

        parts: list[tuple[str, str]] = []
        total_missing = self.subtree_missing(self.graph.root_id)
        parts.append(
            (
                f"mapa · {len(self.graph.nodes)}n · {total_missing} faltan\n\n",
                darkside.MUT,
            )
        )

        for nid, depth in self.visible_rows():
            node = self.graph.nodes[nid]
            has_children = bool(self.graph.children_of(nid))
            if not has_children:
                marker = "  "
            elif nid in self.collapsed:
                marker = "▸ "
            else:
                marker = "▾ "
            missing = self.subtree_missing(nid)
            label = darkside.plain(node.ficha.title or nid)
            indent = "  " * depth
            body = f"{indent}{marker}{label}"
            # Selection is a solid block, and only in the region that has focus —
            # a selection in a dead region would be a second blue run on screen.
            if nid == self.cursor:
                style = (
                    f"bold {darkside.GROUND} on {darkside.ACCENT}"
                    if self.has_focus
                    else f"{darkside.INK} on {darkside.STEP}"
                )
                parts.append((darkside.fit(body, RAIL_WIDTH - 4), style))
            else:
                parts.append((darkside.fit(body, RAIL_WIDTH - 4), darkside.MUT))
            if missing:
                parts.append((f"{missing:>3}", darkside.WARN))
            else:
                parts.append(("   ", ""))
            parts.append(("\n", ""))

        parts.append(("\nterritorio\n", darkside.WORDMARK))
        parts.extend(self._lattice())
        return darkside.Text.assemble(*parts)

    def _lattice(self) -> list[tuple[str, str]]:
        """The constellation field: one dot per node, lit when it is complete.

        Deterministic — it is a picture OF the map, in document order, not a
        decorative random field.
        """
        parts: list[tuple[str, str]] = []
        per_row = (RAIL_WIDTH - 4) // 2
        for i, nid in enumerate(sorted(self.graph.nodes)):
            complete = not self.graph.nodes[nid].ficha.missing_required(self.graph.schema)
            parts.append(("∙ " if complete else "· ", darkside.MUT if complete else darkside.WORDMARK))
            if per_row and (i + 1) % per_row == 0:
                parts.append(("\n", ""))
        have, req = self.graph.coverage()
        pct = round(have / req * 100) if req else 100
        parts.append((f"\n\ncobertura {pct}%", darkside.MUT))
        return parts

    def on_click(self) -> None:
        self.focus()
