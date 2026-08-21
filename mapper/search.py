"""Search index over node titles and ficha content."""
from __future__ import annotations

from .model import Graph


class SearchIndex:
    """Simple in-memory search over the current graph."""

    def __init__(self, graph: Graph):
        self.graph = graph

    def query(self, q: str) -> list[str]:
        return self.graph.search_hits(q)
