"""CSV/TSV import preview: build a Graph from a spreadsheet row-set."""
from __future__ import annotations

import csv
from pathlib import Path

from .mermaid import slugify
from .model import CsvCollision, CsvRow, Edge, Ficha, Graph, Node


def _detect_delimiter(first_line: str) -> str:
    return "\t" if "\t" in first_line else ","


def _park(node: Node) -> None:
    """Mark a node as parked at root because its parent was missing/unknown."""
    if not node.ficha.title.startswith("? "):
        node.ficha.title = f"? {node.ficha.title}"


def preview_csv(path: Path) -> Graph:
    """Return a Graph built from *path* (CSV or TSV).

    Columns:
      - ``id`` becomes the node id. When empty, a slug of ``title`` is used;
        when no slug characters survive (empty or punctuation-only), the next
        ``row-N`` id is used so the row is not dropped.
      - ``title`` becomes the node title; falls back to id.
      - ``parent`` is an id reference to the parent row.
      - ``depth`` is an integer indentation level used when ``parent`` is absent.
      - Any other header is stored in ``ficha.fields`` keyed by header name.

    A blank ``parent`` cell means "no parent": the row is a root candidate. The
    root is the first parentless row that was not parked (if every parentless
    row was parked, the first parentless row). Rows whose parent is
    missing/unknown, and extra parentless rows, are parked under the root with
    their title prefixed by ``"? "`` so they are not silently dropped.
    """
    text = path.read_text(encoding="utf-8")
    if not text:
        return Graph()

    # `line_num` below also counts \x0b \x0c \x1c-\x1e \x85 U+2028 U+2029 as line breaks (ruling R16).
    lines = text.splitlines()
    delimiter = _detect_delimiter(lines[0])
    reader = csv.DictReader(lines, delimiter=delimiter)
    if reader.fieldnames is None:
        return Graph()

    graph = Graph()
    rows: list[tuple[str, str | None, int | None]] = []
    parked: set[str] = set()
    last_at_depth: dict[int, str] = {}
    produced: dict[str, list[CsvRow]] = {}

    # First pass: create nodes so forward parent references resolve.
    auto_counter = 0
    for row in reader:
        raw_id = (row.get("id") or "").strip()
        title = (row.get("title") or "").strip()
        if not raw_id:
            raw_id = title
        nid = slugify(raw_id)
        if not nid:
            auto_counter += 1
            nid = f"row-{auto_counter}"
            raw_id = raw_id or nid
        # LLR-CSV.2.1: record every row that produced this slug, with the
        # line number exactly as `csv.DictReader.line_num` reports it (blank
        # lines and CRLF endings count as the reader counts them) and the id
        # as typed — including auto-generated ids from the empty-id path.
        produced.setdefault(nid, []).append(
            CsvRow(line_no=reader.line_num, raw_id=raw_id)
        )

        title = title if title else raw_id

        parent_cell = (row.get("parent") or "").strip()
        parent_id = slugify(parent_cell) if parent_cell else None
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
        if parent_id is not None:
            if parent_id in graph.nodes:
                graph.add_edge(Edge(parent_id=parent_id, child_id=nid))
            else:
                _park(node)
                parked.add(nid)
        elif depth is not None and depth > 0:
            parent = last_at_depth.get(depth - 1)
            if parent is not None:
                graph.add_edge(Edge(parent_id=parent, child_id=nid))
            else:
                _park(node)
                parked.add(nid)

        if depth is not None:
            last_at_depth[depth] = nid
            for d in list(last_at_depth):
                if d > depth:
                    del last_at_depth[d]

    # Root by parentage, not row order: the first parentless row that was not
    # parked (else the first parentless row; with none, the first row stays).
    # Every other parentless row is attached under it and parked.
    parentless = [nid for nid in graph.nodes if graph.parent_of(nid) is None]
    if parentless:
        root_id = next((n for n in parentless if n not in parked), parentless[0])
        graph.root_id = root_id
        for nid in parentless:
            if nid != root_id:
                graph.add_edge(Edge(parent_id=root_id, child_id=nid))
                _park(graph.nodes[nid])

    # LLR-CSV.2.1: expose every slug more than one row produced — including
    # collisions that violate no loader rule, because the preview keys on the
    # record, not on loader invariants (ruling R1).
    graph.csv_collisions = [
        CsvCollision(slug=nid, rows=tuple(rs))
        for nid, rs in produced.items()
        if len(rs) > 1
    ]

    return graph
