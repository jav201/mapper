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
        """(present required fields, total required fields).

        Counts by asking `missing_required`, which the docstring below calls the
        single owner of "what is missing".  It re-derived that judgement here
        with a bare truthiness test, so the two disagreed on a whitespace-only
        value: the worklist called it missing while the coverage figure counted
        it documented — the quiet inflation US-R03 exists to stop (A-9).
        """
        req = [f for f in schema if f.required]
        return len(req) - len(self.missing_required(schema)), len(req)

    def missing_required(self, schema: list[SchemaField]) -> list[SchemaField]:
        """Required fields this ficha has not filled, in schema order.

        The single owner of "what is missing" (LLR-N01.9).  The inspector, the
        rail's coverage lattice and the coverage worklist all consume this; none
        of them re-derives it, so the three surfaces cannot drift on what
        "complete" means.
        """
        return [f for f in schema if f.required and not self.fields.get(f.key, "").strip()]


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
    source: str = ""
    tags: dict[str, str] = field(default_factory=dict)
    inherited: dict[str, str] = field(default_factory=dict)
    template: bool = False
    path: str = ""  # original office file path, relative to workspace
    kind: str = "text"  # text | docx | pptx | xlsx


@dataclass
class Graph:
    """A navigable structure of nodes and edges."""

    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    root_id: str | None = None
    schema: list[SchemaField] = field(default_factory=list)
    documents: dict[str, Document] = field(default_factory=dict)
    load_warnings: list[str] = field(default_factory=list)

    def document_names(self) -> list[str]:
        """Return all registered document names."""
        return sorted(self.documents.keys())

    def resolve_document(self, name: str, node: Node) -> Document:
        """Return the named document, with its tag maps copied so callers cannot alias them.

        **There is no parent traversal, and its absence is the repair (A-3).**
        `documents` is graph-level and keyed by name — there is no per-node
        document store — so the shipped recursion walked the parent chain
        rebuilding the *same* mapping at every level and returned what it started
        with.  It was a no-op costing one stack frame per level, which is why a
        depth-5000 map raised `RecursionError` inside `FactoryScreen._preview`,
        outside every guard.

        Increment 3 first replaced that recursion with an equivalent *iterative*
        fold.  Review finding F1 established the fold was equally dead: an
        implementation with the whole walk deleted is indistinguishable from it
        over every graph — 173 comparisons, 0 mismatches — so the node certifying
        the traversal could not fail, and the cycle guard it needed had a hang as
        its only regression mode.  The walk is therefore removed rather than
        merely de-recursed: a bounded no-op is still a no-op, and it was carrying
        a guard nothing could test.

        `node` stays in the signature because `FactoryScreen._preview` and the
        document surface both pass it, and because per-node documents are the
        shape this function would take were that store ever added.
        """
        doc = self.documents.get(name)
        if doc is None:
            return Document(name=name, source="")
        return Document(
            name=doc.name,
            source=doc.source,
            tags=dict(doc.tags),
            inherited=dict(doc.inherited),
            template=doc.template,
            path=doc.path,
            kind=doc.kind,
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

    def find_cycle(self) -> list[str] | None:
        """Return one directed cycle's node ids, entry node repeated last.

        Iterative on purpose: the edge set comes from a file, so its depth is
        whatever the file says and recursion would trade one crash for another.
        A node reached twice down *different* branches is a diamond, not a
        cycle, so only an edge back into the currently active path counts.
        """
        children: dict[str, list[str]] = {}
        for edge in self.edges:
            children.setdefault(edge.parent_id, []).append(edge.child_id)

        starts = list(self.nodes) + [p for p in children if p not in self.nodes]
        done: set[str] = set()
        for start in starts:
            if start in done:
                continue
            path = [start]
            on_path = {start}
            stack = [iter(children.get(start, ()))]
            while stack:
                for child in stack[-1]:
                    if child in on_path:
                        return path[path.index(child):] + [child]
                    if child in done:
                        continue
                    path.append(child)
                    on_path.add(child)
                    stack.append(iter(children.get(child, ())))
                    break
                else:
                    stack.pop()
                    finished = path.pop()
                    on_path.discard(finished)
                    done.add(finished)
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
