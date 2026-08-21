"""Core domain model: nodes, edges, graph, fichas, schema, attachments."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SchemaField:
    """One field in a map's customizable schema."""
    key: str
    label: str
    required: bool = False
    kind: str = "text"  # text | date | url | file | image


@dataclass(frozen=True)
class Attachment:
    """A reference attached to a node (never a payload)."""
    kind: str  # file | url | image
    path: str
    caption: str = ""


@dataclass
class Ficha:
    """The information card every node carries."""
    title: str = ""
    state: str = ""  # ok | risk | late | blocked | ""
    meta: str = ""   # short subtitle / status line
    notes: str = ""
    fields: dict[str, str] = field(default_factory=dict)
    attachments: list[Attachment] = field(default_factory=list)

    def required_coverage(self, schema: list[SchemaField]) -> tuple[int, int]:
        """(present required fields, total required fields)."""
        req = [f for f in schema if f.required]
        have = sum(1 for f in req if self.fields.get(f.key))
        return have, len(req)


@dataclass
class Node:
    id: str
    ficha: Ficha = field(default_factory=Ficha)


@dataclass(frozen=True)
class Edge:
    parent_id: str
    child_id: str
    label: str = ""


@dataclass
class Graph:
    """A navigable structure of nodes and edges."""
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    root_id: str | None = None
    schema: list[SchemaField] = field(default_factory=list)

    def add_node(self, node: Node) -> None:
        self.nodes[node.id] = node
        if self.root_id is None:
            self.root_id = node.id

    def add_edge(self, edge: Edge) -> None:
        self.edges.append(edge)

    def children_of(self, node_id: str) -> list[str]:
        return [e.child_id for e in self.edges if e.parent_id == node_id]

    def parent_of(self, node_id: str) -> str | None:
        for e in self.edges:
            if e.child_id == node_id:
                return e.parent_id
        return None

    def focus(self, node_id: str) -> Graph:
        """Return a new graph containing only node_id and its descendants."""
        if node_id not in self.nodes:
            return Graph(schema=self.schema)
        keep = set()
        stack = [node_id]
        while stack:
            current = stack.pop()
            if current in keep:
                continue
            keep.add(current)
            stack.extend(self.children_of(current))
        return Graph(
            nodes={k: v for k, v in self.nodes.items() if k in keep},
            edges=[e for e in self.edges if e.parent_id in keep and e.child_id in keep],
            root_id=node_id,
            schema=self.schema,
        )

    def coverage(self) -> tuple[int, int]:
        """Global coverage across all nodes."""
        have = req = 0
        for node in self.nodes.values():
            h, r = node.ficha.required_coverage(self.schema)
            have += h
            req += r
        return have, req

    def search_hits(self, query: str) -> list[str]:
        """Return node ids whose ficha matches the query (case-insensitive)."""
        q = query.lower()
        hits = []
        for node in self.nodes.values():
            hay = " ".join([
                node.id,
                node.ficha.title,
                node.ficha.meta,
                node.ficha.notes,
                " ".join(node.ficha.fields.values()),
                " ".join(a.caption or a.path for a in node.ficha.attachments),
            ]).lower()
            if q in hay:
                hits.append(node.id)
        return hits
