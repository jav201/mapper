"""CSV/TSV import preview: build a Graph from a spreadsheet row-set."""
from __future__ import annotations

import csv
from pathlib import Path

from .model import Edge, Ficha, Graph, Node


def _detect_delimiter(first_line: str) -> str:
    return "\t" if "\t" in first_line else ","


def _park(node: Node) -> None:
    """Mark a node as parked at root because its parent was missing/unknown."""
    if not node.ficha.title.startswith("? "):
        node.ficha.title = f"? {node.ficha.title}"


def preview_csv(path: Path) -> Graph:
    """Return a Graph built from *path* (CSV or TSV).

    Columns:
      - ``id`` (required) becomes the node id.
      - ``title`` becomes the node title; falls back to id.
      - ``parent`` is an id reference to the parent row.
      - ``depth`` is an integer indentation level used when ``parent`` is absent.
      - Any other header is stored in ``ficha.fields`` keyed by header name.

    Rows whose parent is missing/empty/unknown are parked at the root with their
    title prefixed by ``"? "`` so they are not silently dropped.
    """
    text = path.read_text(encoding="utf-8")
    if not text:
        return Graph()

    lines = text.splitlines()
    delimiter = _detect_delimiter(lines[0])
    reader = csv.DictReader(lines, delimiter=delimiter)
    if reader.fieldnames is None:
        return Graph()

    graph = Graph()
    rows: list[tuple[str, str, str | None, int | None]] = []
    last_at_depth: dict[int, str] = {}

    # First pass: create nodes so forward parent references resolve.
    for row in reader:
        nid = (row.get("id") or "").strip()
        if not nid:
            continue

        title = (row.get("title") or "").strip()
        title = title if title else nid

        parent_id = (row.get("parent") or "").strip()
        depth_raw = (row.get("depth") or "").strip()
        depth = int(depth_raw) if depth_raw.lstrip("-").isdigit() else None

        fields = {}
        for key in row:
            if key in {"id", "title", "parent", "depth"}:
                continue
            if row[key]:
                fields[key] = row[key]

        node = Node(id=nid, ficha=Ficha(title=title, fields=fields))
        graph.add_node(node)
        rows.append((nid, parent_id, depth))

    # Second pass: build edges.
    for nid, parent_id, depth in rows:
        node = graph.nodes[nid]
        if parent_id:
            if parent_id in graph.nodes:
                graph.add_edge(Edge(parent_id=parent_id, child_id=nid))
            else:
                _park(node)
        elif depth is not None and depth > 0:
            parent = last_at_depth.get(depth - 1)
            if parent is not None:
                graph.add_edge(Edge(parent_id=parent, child_id=nid))
            else:
                _park(node)

        if depth is not None:
            last_at_depth[depth] = nid
            for d in list(last_at_depth):
                if d > depth:
                    del last_at_depth[d]

    # Attach remaining orphans to the first declared root.
    root_id = graph.root_id
    if root_id is not None:
        for node in graph.nodes.values():
            if node.id != root_id and graph.parent_of(node.id) is None:
                graph.add_edge(Edge(parent_id=root_id, child_id=node.id))
                _park(node)

    return graph
