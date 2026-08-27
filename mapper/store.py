"""Two-layer persistence: text files as truth, SQLite as rebuildable index."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from .model import Attachment, Document, Edge, Ficha, Graph, Node, SchemaField


class MapStoreError(Exception):
    pass


def _text_attributes() -> tuple[str, ...]:
    """The `Ficha` attributes the model declares as text, derived from the model.

    HLR-R03 (amendment A-7) requires this set to come from `Ficha`'s own
    annotations rather than be named in the requirement or here.  A hand-listed
    set repairs the members that break today and leaves their siblings — which is
    why `state` is in this set even though no consumer joins it.
    """
    return tuple(
        name
        for name, spec in Ficha.__dataclass_fields__.items()
        if spec.type in ("str", str)
    )


# `bool` is a subclass of `int`; it is spelled out for the reader, not the check.
_SCALARS = (str, int, float, bool)


def _coerce_field(graph: Graph, node_id: str, key: str, value: Any) -> str:
    """Return `value` as text, or `""` when it cannot faithfully become text.

    Scalars coerce (LLR-R03.1); containers are refused and recorded
    (LLR-R03.2).  A container must NOT coerce: `str({})` is `"{}"`, a truthy
    string, so `coverage()` would go on counting the malformed field as
    documented and the miscount would survive its own fix.
    """
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    if isinstance(value, _SCALARS):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    graph.load_warnings.append(f"campo ilegible: {node_id}.{key}")
    return ""


TEMPLATES: dict[str, dict[str, Any]] = {
    "legacy-audit": {
        "schema": [
            {"key": "D", "label": "documento", "required": True, "kind": "text"},
            {"key": "O", "label": "dueño", "required": True, "kind": "text"},
            {"key": "E", "label": "estado", "required": True, "kind": "text"},
            {"key": "C", "label": "criticidad", "required": False, "kind": "text"},
            {"key": "N", "label": "notas", "required": False, "kind": "text"},
        ],
        "seed_title": "auditoría legacy",
    }
}


class MapStore:
    """The map lives as `.mmd` + `_nodos.yml`; `mapper.db` is rebuilt from them."""

    def __init__(self, workspace: Path | str):
        self.workspace = Path(workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.db_path = self.workspace / "mapper.db"

    def _text_hash(self, mmd_text: str, yml_text: str) -> str:
        return hashlib.sha256((mmd_text + yml_text).encode()).hexdigest()[:16]

    def _schema_columns(self, conn: sqlite3.Connection, table: str) -> set[str]:
        return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}

    def _needs_recreate(self, conn: sqlite3.Connection) -> bool:
        """Drop and recreate index tables when the on-disk schema is stale."""
        required = {
            "nodes": {"map_id", "id", "parent_id", "title", "state", "meta", "notes"},
            "fields": {"map_id", "node_id", "key", "value"},
            "attachments": {"map_id", "node_id", "kind", "path", "caption"},
            "edges": {"map_id", "parent_id", "child_id", "label"},
        }
        for table, cols in required.items():
            if not cols <= self._schema_columns(conn, table):
                return True
        return False

    def _init_db(self, conn: sqlite3.Connection) -> None:
        if self._needs_recreate(conn):
            conn.executescript(
                "DROP TABLE IF EXISTS edges;"
                "DROP TABLE IF EXISTS attachments;"
                "DROP TABLE IF EXISTS fields;"
                "DROP TABLE IF EXISTS nodes;"
                "DROP TABLE IF EXISTS meta;"
            )
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            CREATE TABLE IF NOT EXISTS nodes (
                map_id TEXT NOT NULL,
                id TEXT NOT NULL,
                parent_id TEXT,
                title TEXT,
                state TEXT,
                meta TEXT,
                notes TEXT,
                PRIMARY KEY (map_id, id)
            );
            CREATE TABLE IF NOT EXISTS fields (
                map_id TEXT NOT NULL,
                node_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                PRIMARY KEY (map_id, node_id, key),
                FOREIGN KEY (map_id, node_id) REFERENCES nodes(map_id, id)
            );
            CREATE TABLE IF NOT EXISTS attachments (
                map_id TEXT NOT NULL,
                node_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                path TEXT NOT NULL,
                caption TEXT,
                FOREIGN KEY (map_id, node_id) REFERENCES nodes(map_id, id)
            );
            CREATE TABLE IF NOT EXISTS edges (
                map_id TEXT NOT NULL,
                parent_id TEXT NOT NULL,
                child_id TEXT NOT NULL,
                label TEXT,
                PRIMARY KEY (map_id, parent_id, child_id),
                FOREIGN KEY (map_id, parent_id) REFERENCES nodes(map_id, id),
                FOREIGN KEY (map_id, child_id) REFERENCES nodes(map_id, id)
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
                    "path": d.path,
                    "kind": d.kind,
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
                path=d.get("path", ""),
                kind=d.get("kind", "text"),
            )
            for d in sidecar.get("documents", [])
            if d.get("name")
        }
        nodes_data = sidecar.get("nodes", {})
        for nid, ndata in nodes_data.items():
            if nid not in graph.nodes:
                graph.add_node(Node(id=nid))
            node = graph.nodes[nid]
            text_attrs = _text_attributes()
            raw_fields = ndata.get("fields", {})
            if not isinstance(raw_fields, dict):
                # LLR-R03.5: a malformed field never denies the map.  A non-dict
                # `fields` is a hand-edited shape `_build_sidecar` cannot produce.
                graph.load_warnings.append(f"campo ilegible: {nid}.fields")
                raw_fields = {}
            node.ficha = Ficha(
                **{
                    attr: _coerce_field(graph, nid, attr, ndata.get(attr, ""))
                    for attr in text_attrs
                },
                fields={
                    key: _coerce_field(graph, nid, key, value)
                    for key, value in raw_fields.items()
                },
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
        try:
            sidecar = yaml.safe_load(yml_text) or {}
        except (yaml.YAMLError, ValueError) as exc:
            # `ValueError` is not redundant beside `YAMLError`: PyYAML's own int
            # constructor calls `int(token)`, and CPython caps integer parsing at
            # `sys.get_int_max_str_digits()` (4300).  A sidecar field with more
            # digits than that raises a BARE ValueError from inside the parser —
            # before any field-level code runs — so the coercion ladder never
            # sees it and cannot defend against it.
            #
            # This is REFUSAL, not repair: the map is still denied, which is
            # `F-M5`'s shape and out of this batch's fence.  What changes is that
            # the refusal is typed, Spanish, and names the file, so it reaches the
            # operator through the same sink as every other load failure instead
            # of escaping as an untyped ValueError.
            raise MapStoreError(
                f"no se pudo leer la ficha de {map_id}: {yml_path.name} ilegible"
            ) from exc
        from .mermaid import CYCLE_ARROW, MermaidError

        try:
            graph = self._graph_from_sidecar(mmd_text, sidecar)
        except MermaidError as exc:
            raise MapStoreError(
                f"el mapa tiene un ciclo: {CYCLE_ARROW.join(exc.cycle)}"
            ) from exc
        self._reindex(map_id, mmd_text, yml_text, graph)
        return graph

    def _atomic_write(self, path: Path, text: str) -> None:
        """Write `text` to `path` atomically via a temp file + rename."""
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)

    def save(self, map_id: str, graph: Graph) -> None:
        mmd_path = self.workspace / f"{map_id}.mmd"
        yml_path = self.workspace / f"{map_id}_nodos.yml"
        from .mermaid import CYCLE_ARROW, dump

        # LLR-R01.5 (A-2): never write what this store's own read side refuses.
        # Increment 1 made `load` reject a cycle; without the symmetric refusal
        # here, `action_save` persists a cyclic preview graph and the very next
        # load — the one `action_save` itself triggers — raises, leaving a file
        # listed with 0 nodes and no in-app route to repair it.  On `master` that
        # file at least loaded, so the asymmetry was worse than the defect.
        cycle = graph.find_cycle()
        if cycle is not None:
            raise MapStoreError(f"el mapa tiene un ciclo: {CYCLE_ARROW.join(cycle)}")

        mmd_text = dump(graph)
        sidecar = self._build_sidecar(graph)
        yml_text = yaml.safe_dump(sidecar, sort_keys=False, allow_unicode=True)
        self._atomic_write(mmd_path, mmd_text)
        self._atomic_write(yml_path, yml_text)
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

    def create_from_template(self, map_id: str, template_id: str) -> Graph:
        """Create a new map seeded from a template definition."""
        template = TEMPLATES.get(template_id)
        if template is None:
            raise MapStoreError(f"Template not found: {template_id}")

        graph = Graph()
        graph.schema = [
            SchemaField(
                key=f.get("key", ""),
                label=f.get("label", ""),
                required=f.get("required", False),
                kind=f.get("kind", "text"),
            )
            for f in template.get("schema", [])
        ]
        root = Node(
            id="root",
            ficha=Ficha(title=template.get("seed_title", map_id)),
        )
        graph.add_node(root)
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
        hash_key = f"hash:{map_id}"
        conn = sqlite3.connect(self.db_path)
        try:
            self._init_db(conn)
            stored = conn.execute("SELECT value FROM meta WHERE key=?", (hash_key,)).fetchone()
            if stored and stored[0] == text_hash:
                return
            # Delete child rows before parent rows to avoid FK violations.
            conn.execute("DELETE FROM edges WHERE map_id=?", (map_id,))
            conn.execute("DELETE FROM attachments WHERE map_id=?", (map_id,))
            conn.execute("DELETE FROM fields WHERE map_id=?", (map_id,))
            conn.execute("DELETE FROM nodes WHERE map_id=?", (map_id,))
            for node in graph.nodes.values():
                parent = graph.parent_of(node.id)
                conn.execute(
                    "INSERT OR REPLACE INTO nodes (map_id, id, parent_id, title, state, meta, notes) VALUES (?,?,?,?,?,?,?)",
                    (map_id, node.id, parent, node.ficha.title, node.ficha.state, node.ficha.meta, node.ficha.notes),
                )
                for k, v in node.ficha.fields.items():
                    conn.execute(
                        "INSERT OR REPLACE INTO fields (map_id, node_id, key, value) VALUES (?,?,?,?)",
                        (map_id, node.id, k, v),
                    )
                for a in node.ficha.attachments:
                    conn.execute(
                        "INSERT INTO attachments (map_id, node_id, kind, path, caption) VALUES (?,?,?,?,?)",
                        (map_id, node.id, a.kind, a.path, a.caption),
                    )
            for edge in graph.edges:
                conn.execute(
                    "INSERT OR REPLACE INTO edges (map_id, parent_id, child_id, label) VALUES (?,?,?,?)",
                    (map_id, edge.parent_id, edge.child_id, edge.label),
                )
            conn.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES (?,?)",
                (hash_key, text_hash),
            )
            conn.commit()
        finally:
            conn.close()
