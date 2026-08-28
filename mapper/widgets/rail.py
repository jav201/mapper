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
        # RENDERED, NOT OWNED (LLR-N06.2.1).  The rail used to hold a
        # `collapsed` set and a `toggle` that mutated it, which made fold state
        # live inside a widget `_apply_region_visibility` auto-hides below 118
        # columns -- so the canvas could not read it and the two surfaces could
        # disagree about what was folded.  `MapScreen` owns the set now; this
        # attribute is only the last value it was handed.
        self.folded: frozenset[str] = frozenset()

    def show(self, graph: Graph, cursor: str | None,
             folded: frozenset[str]) -> None:
        self.graph = graph
        self.cursor = cursor
        self.folded = folded
        self.refresh()

    # -- structure ---------------------------------------------------------
    def _child_index(self) -> dict[str, list[str]]:
        """Adjacency built once. `Graph.children_of` rescans every edge per call."""
        index: dict[str, list[str]] = {}
        for edge in self.graph.edges:
            index.setdefault(edge.parent_id, []).append(edge.child_id)
        return index

    def visible_rows(self) -> list[tuple[str, int]]:
        """`(node_id, depth)` for every row the rail currently shows."""
        if self.graph.root_id is None:
            return []
        return self._rows(self._child_index())

    def _rows(self, index: dict[str, list[str]]) -> list[tuple[str, int]]:
        """Pre-order over an explicit stack, left to right, exactly as before.

        `visiting` is the active path.  The recursion this replaces answered a
        cyclic graph with a RecursionError; a plain loop would answer it by
        never returning, and a hang is worse than a crash — the lesson
        increment 2 paid for at 23.7 GB resident.
        """
        rows: list[tuple[str, int]] = []
        visiting: set[str] = set()
        stack: list[tuple[str, int, bool]] = [(self.graph.root_id, 0, False)]
        while stack:
            nid, depth, leaving = stack.pop()
            if leaving:
                visiting.discard(nid)
                continue
            if nid in visiting:
                raise ValueError(f"cycle through {nid}: the graph is not a tree")
            rows.append((nid, depth))
            if nid in self.folded:
                continue
            children = index.get(nid)
            if not children:
                continue
            visiting.add(nid)
            stack.append((nid, depth, True))
            # Reversed, so the LIFO stack still emits left to right.
            stack.extend((cid, depth + 1, False) for cid in reversed(children))
        return rows

    def subtree_missing(self, node_id: str) -> int:
        """How many required fields are unfilled in this branch, including itself.

        Consumes `Ficha.missing_required` — the model owns that definition, so the
        rail and the coverage worklist cannot disagree about what is complete.

        Deliberately the exact walk and NOT `_missing_map`: this is a public
        method scoped to one subtree, and `_missing_map` visits every node in the
        graph, so routing through it made a caller asking about a clean branch
        raise for a cycle in a component it never asked about — and turned an
        `O(subtree)` question into `O(N+E)`.  `_body` still uses the memoised map,
        which is where the cost actually mattered: it asked this question once per
        visible row.  (Increment 2b review, finding F2.)
        """
        return self._missing_walk(node_id, self._child_index())

    def _missing_walk(self, node_id: str, index: dict[str, list[str]]) -> int:
        """The exact answer: one deduplicated walk of this node's reachable set."""
        total = 0
        stack = [node_id]
        seen: set[str] = set()
        while stack:
            nid = stack.pop()
            if nid in seen or nid not in self.graph.nodes:
                continue
            seen.add(nid)
            total += len(self.graph.nodes[nid].ficha.missing_required(self.graph.schema))
            stack.extend(index.get(nid, ()))
        return total

    def _missing_map(self, index: dict[str, list[str]]) -> dict[str, int] | None:
        """Missing-per-subtree for every node in one post-order pass, or `None`.

        `None` means the graph is not a forest, and a forest is the only shape
        where this pass equals `_missing_walk`: where two paths reach one node
        the walk counts its gaps once and a post-order sum counts them twice.
        `mermaid.parse` refuses multiple parents and a CSV preview gives every
        node one parent, so the exact walk stays the answer for a shape that
        cannot arrive — rather than this pass answering it wrong and fast.

        The shipped code called `subtree_missing` once per visible row, each
        call re-walking the branch through `children_of`, which rescans every
        edge.  Measured on a chain: 0.016 s at depth 100, 5.616 s at depth 800.
        """
        parents: dict[str, int] = {}
        for edge in self.graph.edges:
            parents[edge.child_id] = parents.get(edge.child_id, 0) + 1
            if parents[edge.child_id] > 1:
                return None

        nodes = self.graph.nodes
        own = {
            nid: len(node.ficha.missing_required(self.graph.schema))
            for nid, node in nodes.items()
        }
        totals: dict[str, int] = {}
        visiting: set[str] = set()
        for start in nodes:
            if start in totals:
                continue
            stack: list[tuple[str, bool]] = [(start, False)]
            while stack:
                nid, expanded = stack.pop()
                children = [cid for cid in index.get(nid, ()) if cid in nodes]
                if expanded:
                    visiting.discard(nid)
                    totals[nid] = own[nid] + sum(totals[cid] for cid in children)
                    continue
                if nid in totals:
                    continue
                if nid in visiting:
                    raise ValueError(f"cycle through {nid}: the graph is not a tree")
                if not children:
                    totals[nid] = own[nid]
                    continue
                visiting.add(nid)
                stack.append((nid, True))
                stack.extend((cid, False) for cid in children)
        return totals

    # -- rendering ---------------------------------------------------------
    def render(self):
        """Converts the cycle guard into a painted notice instead of propagating.

        `MapScreen.refresh_canvas` wraps `renderer.render(...)` only, so an
        exception raised here escapes the Textual message pump and takes the
        application with it — defect S-01a's shape, one widget over
        (amendment A-6).  A cyclic graph reaches the rail through the CSV
        preview door, which never passes `mermaid.parse`.

        It catches `ValueError`, which is the guard's own type, and NOT every
        exception: a malformed graph carrying an edge to an absent node still
        raises `KeyError` from `_body`, exactly as it does on `master`.  The
        earlier docstring claimed this "never propagates", which was wider than
        the code and wider than the requirement.  (Increment 2b review, F5.)
        """
        try:
            return self._body()
        except ValueError:
            return darkside.Text.assemble(
                (
                    "  no se puede dibujar:\n  el mapa tiene un ciclo",
                    darkside.ALERT,
                )
            )

    def _body(self):
        if self.graph.root_id is None:
            return darkside.Text.assemble(("  (mapa vacío)", darkside.MUT))

        index = self._child_index()
        rows = self._rows(index)
        totals = self._missing_map(index)
        if totals is None:
            needed = {self.graph.root_id, *(nid for nid, _ in rows)}
            totals = {nid: self._missing_walk(nid, index) for nid in needed}

        parts: list[tuple[str, str]] = []
        total_missing = totals.get(self.graph.root_id, 0)
        parts.append(
            (
                f"mapa · {len(self.graph.nodes)}n · {total_missing} faltan\n\n",
                darkside.MUT,
            )
        )

        for nid, depth in rows:
            node = self.graph.nodes[nid]
            has_children = bool(index.get(nid))
            if not has_children:
                marker = "  "
            elif nid in self.folded:
                marker = "▸ "
            else:
                marker = "▾ "
            missing = totals.get(nid, 0)
            label = darkside.plain(node.ficha.title or nid)
            # `fit` truncates to RAIL_WIDTH - 4 cells, so any indent already
            # past that width produces the same row however much wider it gets.
            # Building the true indent instead makes a deep chain quadratic in
            # characters: 3.257 s at depth 5000, against 0.093 s capped.
            indent = "  " * min(depth, RAIL_WIDTH)
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
