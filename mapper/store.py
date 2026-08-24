"""Two-layer persistence: text files as truth, SQLite as rebuildable index."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

import yaml

from .model import Attachment, Document, Edge, Ficha, Graph, Node, SchemaField


class MapStoreError(Exception):
    pass


class MapStore:
    """The map lives as `.mmd` + `_nodos.yml`; `mapper.db` is rebuilt from them."""

    def __init__(self, workspace: Path | str):
        self.workspace = Path(workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.db_path = self.workspace / "mapper.db"

    def _text_hash(self, mmd_text: str, yml_text: str) -> str:
        return hashlib.sha256((mmd_text + yml_text).encode()).hexdigest()[:16]

    def _init_db(self, conn: sqlite3.Connection) -> None:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                map_id TEXT NOT NULL,
                parent_id TEXT,
                title TEXT,
                state TEXT,
                meta TEXT,
                notes TEXT
            );
            CREATE TABLE IF NOT EXISTS fields (
                node_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                PRIMARY KEY (node_id, key)
            );
            CREATE TABLE IF NOT EXISTS attachments (
                node_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                path TEXT NOT NULL,
                caption TEXT
            );
            CREATE TABLE IF NOT EXISTS edges (
                parent_id TEXT NOT NULL,
                child_id TEXT NOT NULL,
                label TEXT,
                PRIMARY KEY (parent_id, child_id)
            );
            """
        )

    def _sidecar_to_dict(self, sidecar: dict[str, Any]) -> dict[str, Any]:
        return sidecar

    def _build_sidecar(self, graph: Graph) -> dict[str, Any]:
        """Serialize graph schema + fichas + documents to sidecar dict."""
        sidecar: dict[str, Any] = {
            "schema": [
                {"key": f.key, "label": f.label, "required": f.required, "kind": f.kind}
                for f in graph.schema
            ],
            "documents": [
                {
                    "name": d.name,
                    "source": d.source,
                    "tags": d.tags,
                    "inherited": d.inherited,
                    "template": d.template,
                }
                for d in graph.documents.values()
            ],
            "nodes": {},
        }
        for node in graph.nodes.values():
            sidecar["nodes"][node.id] = {
                "title": node.ficha.title,
                "state": node.ficha.state,
                "meta": node.ficha.meta,
                "notes": node.ficha.notes,
                "fields": node.ficha.fields,
                "attachments": [
                    {"kind": a.kind, "path": a.path, "caption": a.caption}
                    for a in node.ficha.attachments
                ],
            }
        return sidecar

    def _graph_from_sidecar(
        self, mmd_text: str, sidecar: dict[str, Any]
    ) -> Graph:
        """Build a Graph from mermaid text + sidecar."""
        from .mermaid import parse

        graph = parse(mmd_text)
        schema = [
            SchemaField(
                key=f.get("key", ""),
                label=f.get("label", ""),
                required=f.get("required", False),
                kind=f.get("kind", "text"),
            )
            for f in sidecar.get("schema", [])
        ]
        graph.schema = schema
        graph.documents = {
            d.get("name", ""): Document(
                name=d.get("name", ""),
                source=d.get("source", ""),
                tags=d.get("tags", {}),
                inherited=d.get("inherited", {}),
                template=d.get("template", False),
            )
            for d in sidecar.get("documents", [])
            if d.get("name")
        }
        nodes_data = sidecar.get("nodes", {})
        for nid, ndata in nodes_data.items():
            if nid not in graph.nodes:
                graph.add_node(Node(id=nid))
            node = graph.nodes[nid]
            node.ficha = Ficha(
                title=ndata.get("title", ""),
                state=ndata.get("state", ""),
                meta=ndata.get("meta", ""),
                notes=ndata.get("notes", ""),
                fields=ndata.get("fields", {}),
                attachments=[
                    Attachment(kind=a["kind"], path=a["path"], caption=a.get("caption", ""))
                    for a in ndata.get("attachments", [])
                ],
            )
        return graph

    def load(self, map_id: str) -> Graph:
        mmd_path = self.workspace / f"{map_id}.mmd"
        yml_path = self.workspace / f"{map_id}_nodos.yml"
        if not mmd_path.exists():
            raise MapStoreError(f"Map not found: {mmd_path}")
        mmd_text = mmd_path.read_text(encoding="utf-8")
        yml_text = yml_path.read_text(encoding="utf-8") if yml_path.exists() else "{}"
        sidecar = yaml.safe_load(yml_text) or {}
        graph = self._graph_from_sidecar(mmd_text, sidecar)
        self._reindex(map_id, mmd_text, yml_text, graph)
        return graph

    def save(self, map_id: str, graph: Graph) -> None:
        mmd_path = self.workspace / f"{map_id}.mmd"
        yml_path = self.workspace / f"{map_id}_nodos.yml"
        from .mermaid import dump

        mmd_text = dump(graph)
        sidecar = self._build_sidecar(graph)
        yml_text = yaml.safe_dump(sidecar, sort_keys=False, allow_unicode=True)
        mmd_path.write_text(mmd_text, encoding="utf-8")
        yml_path.write_text(yml_text, encoding="utf-8")
        self._reindex(map_id, mmd_text, yml_text, graph)

    def create_seed(self, map_id: str) -> Graph:
        """Create a new map with a small demo tree so it is immediately navigable."""
        graph = Graph()
        root = Node(id="root", ficha=Ficha(title=map_id, meta="nuevo mapa"))
        graph.add_node(root)
        child_a = Node(id="n1", ficha=Ficha(title="primer hijo", meta="presiona l"))
        child_b = Node(id="n2", ficha=Ficha(title="segundo hijo", meta="navega con j/k"))
        graph.add_node(child_a)
        graph.add_node(child_b)
        graph.add_edge(Edge(parent_id="root", child_id="n1"))
        graph.add_edge(Edge(parent_id="root", child_id="n2"))
        self.save(map_id, graph)
        return graph

    def _state_path(self) -> Path:
        state_dir = self.workspace / ".mapper"
        state_dir.mkdir(parents=True, exist_ok=True)
        return state_dir / "state.json"

    def record_session(self, map_id: str, node_id: str | None) -> None:
        """Persist the most recently visited map and node."""
        state = {"map_id": map_id, "node_id": node_id}
        self._state_path().write_text(json.dumps(state), encoding="utf-8")

    def last_session(self) -> tuple[str | None, str | None]:
        """Return the most recently visited (map_id, node_id), if any."""
        path = self._state_path()
        if not path.exists():
            return (None, None)
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
            return (state.get("map_id"), state.get("node_id"))
        except (json.JSONDecodeError, OSError):
            return (None, None)

    def _reindex(self, map_id: str, mmd_text: str, yml_text: str, graph: Graph) -> None:
        text_hash = self._text_hash(mmd_text, yml_text)
        conn = sqlite3.connect(self.db_path)
        try:
            self._init_db(conn)
            stored = conn.execute("SELECT value FROM meta WHERE key='hash'").fetchone()
            if stored and stored[0] == text_hash:
                return
            conn.execute("DELETE FROM nodes WHERE map_id=?", (map_id,))
            conn.execute("DELETE FROM fields WHERE node_id IN (SELECT id FROM nodes WHERE map_id=?)", (map_id,))
            conn.execute("DELETE FROM attachments WHERE node_id IN (SELECT id FROM nodes WHERE map_id=?)", (map_id,))
            conn.execute("DELETE FROM edges WHERE parent_id IN (SELECT id FROM nodes WHERE map_id=?)", (map_id,))
            for node in graph.nodes.values():
                parent = graph.parent_of(node.id)
                conn.execute(
                    "INSERT OR REPLACE INTO nodes (id, map_id, parent_id, title, state, meta, notes) VALUES (?,?,?,?,?,?,?)",
                    (node.id, map_id, parent, node.ficha.title, node.ficha.state, node.ficha.meta, node.ficha.notes),
                )
                for k, v in node.ficha.fields.items():
                    conn.execute(
                        "INSERT OR REPLACE INTO fields (node_id, key, value) VALUES (?,?,?)",
                        (node.id, k, v),
                    )
                for a in node.ficha.attachments:
                    conn.execute(
                        "INSERT INTO attachments (node_id, kind, path, caption) VALUES (?,?,?,?)",
                        (node.id, a.kind, a.path, a.caption),
                    )
            for edge in graph.edges:
                conn.execute(
                    "INSERT OR REPLACE INTO edges (parent_id, child_id, label) VALUES (?,?,?)",
                    (edge.parent_id, edge.child_id, edge.label),
                )
            conn.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES (?,?)",
                ("hash", text_hash),
            )
            conn.commit()
        finally:
            conn.close()
