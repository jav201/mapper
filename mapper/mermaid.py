"""Mermaid `graph TD` round-trip: parse and dump."""
from __future__ import annotations

import re

from .model import Edge, Graph, Node


class ParseError(Exception):
    pass


_MERMAID_EDGE = re.compile(
    r"([\w-]+)(?:\[([^\]]*)\])?\s*-->(?:\|([^|]*)\|)?\s*([\w-]+)(?:\[([^\]]*)\])?"
)
_MERMAID_NODE = re.compile(r"([\w-]+)(?:\[([^\]]*)\])?")


def slugify(value: str) -> str:
    """Return a safe mermaid id: lowercase, hyphens/underscores allowed."""
    value = value.lower().strip()
    value = re.sub(r"[^\w\s-]", "-", value)
    value = re.sub(r"[-\s]+", "-", value).strip("-")
    return value[:32] or "n"


def _ensure_node(nodes: dict[str, Node], nid: str, label: str | None) -> None:
    if nid not in nodes:
        nodes[nid] = Node(id=nid)
    if label is not None:
        nodes[nid].ficha.title = label or nid


def parse(src: str) -> Graph:
    """Parse the MVP subset of `graph TD`: bare ids, labelled nodes, edge labels.

    Multiple parents raise ParseError because the MVP graph is a tree.
    """
    nodes: dict[str, Node] = {}
    children_by_parent: dict[str, list[str]] = {}
    child_to_parent: dict[str, str] = {}
    root_id: str | None = None

    for line_no, raw in enumerate(src.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("%%"):
            continue
        if line.lower().startswith("graph"):
            continue

        m = _MERMAID_EDGE.search(line)
        if m:
            pid, plabel, edge_label, cid, clabel = m.groups()
            _ensure_node(nodes, pid, plabel)
            _ensure_node(nodes, cid, clabel)
            if cid in child_to_parent:
                raise ParseError(
                    f"Line {line_no}: node '{cid}' has multiple parents (out of MVP scope)"
                )
            child_to_parent[cid] = pid
            children_by_parent.setdefault(pid, []).append(cid)
            if root_id is None:
                root_id = pid
            continue

        nm = _MERMAID_NODE.fullmatch(line)
        if nm:
            nid, label = nm.groups()
            _ensure_node(nodes, nid, label)
            if root_id is None:
                root_id = nid
            continue

        raise ParseError(f"Line {line_no}: unsupported syntax: {raw!r}")

    if root_id is None:
        return Graph()

    # Pick a real root: a node with no parent, preferring the first declared root.
    candidates = [nid for nid in nodes if nid not in child_to_parent]
    if candidates:
        root_id = candidates[0]
    else:
        # Cycle or single self-edge; fall back to first node.
        root_id = next(iter(nodes))

    # Build edges
    edges: list[Edge] = []
    for pid, cids in children_by_parent.items():
        for cid in cids:
            edges.append(Edge(parent_id=pid, child_id=cid, label=""))

    graph = Graph(nodes=nodes, edges=edges, root_id=root_id)
    return graph


def dump(graph: Graph) -> str:
    """Dump the graph to `graph TD` notation."""
    lines = ["graph TD"]
    emitted: set[str] = set()
    for edge in graph.edges:
        p = graph.nodes.get(edge.parent_id)
        c = graph.nodes.get(edge.child_id)
        if p is None or c is None:
            continue
        plabel = p.ficha.title if p.ficha.title and p.ficha.title != p.id else ""
        clabel = c.ficha.title if c.ficha.title and c.ficha.title != c.id else ""
        left = f"{p.id}[{plabel}]" if plabel else p.id
        right = f"{c.id}[{clabel}]" if clabel else c.id
        arrow = " --> "
        if edge.label:
            arrow = f" -->|{edge.label}| "
        line = f"    {left}{arrow}{right}"
        if line not in emitted:
            lines.append(line)
            emitted.add(line)
    # Emit orphan nodes (no edges) so they are not lost
    for node in graph.nodes.values():
        if not any(e.parent_id == node.id or e.child_id == node.id for e in graph.edges):
            label = node.ficha.title if node.ficha.title and node.ficha.title != node.id else ""
            line = f"    {node.id}[{label}]" if label else f"    {node.id}"
            if line not in emitted:
                lines.append(line)
                emitted.add(line)
    return "\n".join(lines) + "\n"
