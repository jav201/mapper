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

    def linked_map_id(self) -> str | None:
        """Return the target map id if this node links to another map."""
        value = self.ficha.fields.get("map", "").strip()
        return value if value else None


@dataclass(frozen=True)
class Edge:
    parent_id: str
    child_id: str
    label: str = ""


@dataclass
class Document:
    """A document template attached to a node or inherited from a parent."""

    name: str
    source: str
    tags: dict[str, str] = field(default_factory=dict)
    inherited: dict[str, str] = field(default_factory=dict)
    template: bool = False


@dataclass
class Graph:
    """A navigable structure of nodes and edges."""

    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    root_id: str | None = None
    schema: list[SchemaField] = field(default_factory=list)
    documents: dict[str, Document] = field(default_factory=dict)

    def document_names(self) -> list[str]:
        """Return all registered document names."""
        return sorted(self.documents.keys())

    def resolve_document(self, name: str, node: Node) -> Document:
        """Return a document with missing local tags filled from the parent node's same-named document, if any."""
        doc = self.documents.get(name)
        if doc is None:
            return Document(name=name, source="")
        merged_tags = dict(doc.tags)
        merged_inherited = dict(doc.inherited)
        parent_id = self.parent_of(node.id)
        if parent_id is not None:
            parent = self.nodes.get(parent_id)
            if parent is not None:
                parent_doc = self.resolve_document(name, parent)
                for key, value in parent_doc.tags.items():
                    if key not in merged_tags:
                        merged_tags[key] = value
                        merged_inherited[key] = value
        return Document(
            name=doc.name,
            source=doc.source,
            tags=merged_tags,
            inherited=merged_inherited,
            template=doc.template,
        )

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
            documents=self.documents,
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
