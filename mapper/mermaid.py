"""Mermaid `graph TD` round-trip: parse and dump."""
from __future__ import annotations

import re

from .model import Edge, Graph, Node


class ParseError(Exception):
    pass


# U+2192 RIGHTWARDS ARROW: the separator the cycle path is reported with.
CYCLE_ARROW = chr(0x2192)


class MermaidError(ParseError):
    """A mermaid source whose edge set contains a directed cycle.

    Carries the cycle itself, not only prose about it, so `MapStore.load` can
    restate the path in Spanish without re-parsing this exception's text.
    """

    def __init__(self, cycle: list[str]):
        super().__init__(f"the map has a cycle: {CYCLE_ARROW.join(cycle)}")
        self.cycle = cycle


_MERMAID_EDGE = re.compile(
    r"([\w-]+)(?:\[([^\]]*)\])?\s*-->(?:\|([^|]*)\|)?\s*([\w-]+)(?:\[([^\]]*)\])?"
)
_MERMAID_NODE = re.compile(r"([\w-]+)(?:\[([^\]]*)\])?")


def _escape_mermaid(value: str) -> str:
    """Escape characters that break mermaid node/edge labels."""
    return value.replace("]", "#93;").replace("|", "#124;")


def _unescape_mermaid(value: str) -> str:
    """Restore characters escaped by `_escape_mermaid`."""
    return value.replace("#93;", "]").replace("#124;", "|")


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
    edge_labels: dict[tuple[str, str], str] = {}
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
            _ensure_node(nodes, pid, _unescape_mermaid(plabel) if plabel else plabel)
            _ensure_node(nodes, cid, _unescape_mermaid(clabel) if clabel else clabel)
            if cid in child_to_parent:
                raise ParseError(
                    f"Line {line_no}: node '{cid}' has multiple parents (out of MVP scope)"
                )
            child_to_parent[cid] = pid
            children_by_parent.setdefault(pid, []).append(cid)
            if edge_label:
                edge_labels[(pid, cid)] = _unescape_mermaid(edge_label)
            if root_id is None:
                root_id = pid
            continue

        nm = _MERMAID_NODE.fullmatch(line)
        if nm:
            nid, label = nm.groups()
            _ensure_node(nodes, nid, _unescape_mermaid(label) if label else label)
            if root_id is None:
                root_id = nid
            continue

        raise ParseError(f"Line {line_no}: unsupported syntax: {raw!r}")

    if root_id is None:
        return Graph()

    # Build edges
    edges: list[Edge] = []
    for pid, cids in children_by_parent.items():
        for cid in cids:
            label = edge_labels.get((pid, cid), "")
            edges.append(Edge(parent_id=pid, child_id=cid, label=label))

    graph = Graph(nodes=nodes, edges=edges)
    cycle = graph.find_cycle()
    if cycle is not None:
        raise MermaidError(cycle)

    # Pick a real root: a node with no parent, preferring the first declared root.
    # Acyclic and non-empty, so at least one parentless node exists.
    graph.root_id = [nid for nid in nodes if nid not in child_to_parent][0]
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
        plabel = _escape_mermaid(p.ficha.title) if p.ficha.title and p.ficha.title != p.id else ""
        clabel = _escape_mermaid(c.ficha.title) if c.ficha.title and c.ficha.title != c.id else ""
        left = f"{p.id}[{plabel}]" if plabel else p.id
        right = f"{c.id}[{clabel}]" if clabel else c.id
        arrow = " --> "
        if edge.label:
            arrow = f" -->|{_escape_mermaid(edge.label)}| "
        line = f"    {left}{arrow}{right}"
        if line not in emitted:
            lines.append(line)
            emitted.add(line)
    # Emit orphan nodes (no edges) so they are not lost
    for node in graph.nodes.values():
        if not any(e.parent_id == node.id or e.child_id == node.id for e in graph.edges):
            label = _escape_mermaid(node.ficha.title) if node.ficha.title and node.ficha.title != node.id else ""
            line = f"    {node.id}[{label}]" if label else f"    {node.id}"
            if line not in emitted:
                lines.append(line)
                emitted.add(line)
    return "\n".join(lines) + "\n"
