"""Two-layer persistence: text files as truth, SQLite as rebuildable index."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import MISSING
from datetime import date, datetime
from pathlib import Path
from typing import Any, get_type_hints

import yaml

from .model import Attachment, Document, Edge, Ficha, Graph, Node, SchemaField


class MapStoreError(Exception):
    pass


def _text_fields(cls: type) -> tuple[str, ...]:
    """The attributes `cls` declares as text, derived from the model.

    HLR-R03 (amendment A-7) requires this set to come from the dataclass's own
    annotations rather than be named in the requirement or here.  A hand-listed
    set repairs the members that break today and leaves their siblings — which is
    why `state` is in `Ficha`'s set even though no consumer joins it.

    LLR-STO.1.1 generalises this from `Ficha` alone to every dataclass
    `_build_sidecar` round-trips.  The narrow version was the defect: it was a
    correct derivation applied to ONE of the four dataclasses, so `Attachment`,
    `SchemaField` and `Document` were hand-constructed two lines below it and
    stayed raw.  Measured at `d877784`: 12 of 17 text positions leaked a non-`str`
    past the boundary.
    """
    return tuple(
        name
        for name, spec in cls.__dataclass_fields__.items()
        if spec.type in ("str", str)
    )


def _text_attributes() -> tuple[str, ...]:
    """`Ficha`'s text attributes.  Retained: it is the name the shipped tests use."""
    return _text_fields(Ficha)


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


def _coerce_text_fields(
    graph: Graph, owner: str, cls: type, data: dict[str, Any]
) -> dict[str, Any]:
    """Coerce every text field `cls` declares, leaving its non-text fields alone.

    LLR-STO.1.1.  The set of fields comes from `_text_fields(cls)`, so adding a
    `str` field to any of these dataclasses extends the coercion automatically.
    That is the whole point: the previous shape was a correct derivation wired to
    one dataclass, which is indistinguishable from a hand-listed set everywhere
    else.
    """
    specs = cls.__dataclass_fields__
    out: dict[str, Any] = {}
    for name in _text_fields(cls):
        # The dataclass's OWN default, not a hard-coded `""`.  `SchemaField.kind`
        # and `Document.kind` default to `"text"`; defaulting them to `""` here
        # would rewrite a `kind`-less legacy sidecar on the next save, which is a
        # behaviour change no requirement asked for (Inc-1 review, F2).
        default = specs[name].default
        if default is MISSING:
            default = ""
        out[name] = _coerce_field(graph, owner, name, data.get(name, default))
    return out


def _str_map_fields(cls: type) -> tuple[str, ...]:
    """The attributes `cls` declares as `dict[str, str]` — text on BOTH sides.

    `_text_fields` selects scalar annotations and necessarily misses these, but a
    `dict[str, str]` that `_build_sidecar` round-trips verbatim is two text
    positions per entry, not zero.  `Ficha.fields` is the same shape and has always
    been coerced; excluding `Document.tags`/`inherited` was a HAND EXCLUSION on a
    reason that did not distinguish them from `fields` (whole-branch QA, HIGH-1).

    The annotation is RESOLVED, not spelled-matched.  Under `from __future__ import
    annotations` every annotation is a string, and a textual match reads
    `Dict[str, str]`, `Mapping[str, str]`, a type alias and a quoted annotation as
    non-matches: such a field would fall out of the coercion AND out of the census
    that guards it, simultaneously and silently.  That is HIGH-1's own mechanism one
    level down (confirmation review, MEDIUM-C).

    Scope, stated exactly rather than generally -- the previous wording here claimed
    "any round-tripped dataclass" and was FALSE against disk, which is the same
    defect F2 fixed in this commit.  This function's only caller is
    `_graph_from_sidecar`'s `Document` branch, so it extends `Document`'s coercion
    automatically.  `Ficha.fields` is coerced at its own site, whose record
    coordinates differ (`{nid}.{key}` against `document[i].{field}.{key}`) and are
    pinned by shipped arms, so routing it through here would be a behaviour change,
    not a cleanup.  No other round-tripped dataclass declares a `dict[str, str]`
    today, and `test_at_p02i` fails loudly if one appears.
    """
    hints = get_type_hints(cls)
    return tuple(n for n in cls.__dataclass_fields__ if hints[n] == dict[str, str])


def _coerce_str_map(graph: Graph, owner: str, key: str, value: Any) -> dict[str, str]:
    """Coerce a `dict[str, str]`, refusing-and-recording on BOTH sides.

    Same ladder, same sink, same collision handling as the node `fields` map --
    because it is the same shape, and treating it differently is precisely what
    produced HIGH-1.
    """
    if not isinstance(value, dict):
        graph.load_warnings.append(f"campo ilegible: {owner}.{key}")
        return {}
    out: dict[str, str] = {}
    for raw_key, raw_value in value.items():
        ckey = _coerce_field(graph, owner, f"{key}[{raw_key!r}]", raw_key)
        if ckey in out:
            graph.load_warnings.append(
                f"campo duplicado: {owner}.{key}.{ckey!r} <- {raw_key!r}"
            )
        out[ckey] = _coerce_field(graph, owner, f"{key}.{raw_key}", raw_value)
    return out


def _mappings(
    graph: Graph, owner: str, key: str, entries: Any
) -> list[dict[str, Any]]:
    """The mapping entries of `entries`, recording every non-mapping it refuses.

    LLR-STO.1.1 threshold 2 requires a refusal to be RECORDED, never silent.
    Filtering a malformed entry out without a record destroys operator data on the
    next save, because the read side is the only thing that reconstructs
    `_build_sidecar`'s input (Inc-1 review, F1).

    Scoped to `attachments` DELIBERATELY, and the asymmetry is OBSERVABLE, not a
    preference: a malformed `attachments` entry used to be DISCARDED SILENTLY and
    the map still loaded, so the operator lost it with nothing anywhere saying so.
    A malformed `schema`/`documents` entry has never been silent -- it escapes to
    the typed-refusal net and the load is DENIED with a `MapStoreError`.  Loud
    denial is already a report; silent discard is not.  Routing the denied families
    through here would convert a denial into a warning -- a behaviour change no
    finding asked for -- and would take three arms off the net's counterfactual.
    Measured (review Q1): schema/document item-scalars are denied typed; only
    attachments carried the silent-loss class.
    """
    if not isinstance(entries, list):
        graph.load_warnings.append(f"campo ilegible: {owner}.{key}")
        return []
    out = []
    for i, entry in enumerate(entries):
        if isinstance(entry, dict):
            out.append(entry)
        else:
            # The index is part of the record.  Without it n malformed entries
            # emit n byte-identical lines that cannot be told apart -- the same
            # diagnostic defect F7 fixed for field keys (review G4).
            graph.load_warnings.append(f"campo ilegible: {owner}.{key}[{i}]")
    return out


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
        # LLR-STO.1.1: every dataclass `_build_sidecar` round-trips is coerced
        # through the same ladder.  `required` and `template` are `bool`, so
        # `_text_fields` correctly leaves them.
        #
        # `tags`/`inherited` are `dict[str, str]` -- TEXT ON BOTH SIDES, and
        # round-tripped verbatim, so they are four more text positions, not zero.
        # They were excluded on the reasoning that they "are dicts by design",
        # which is equally true of `Ficha.fields` -- which has always been coerced.
        # A hand exclusion that does not distinguish its members from a covered
        # sibling is the C-31 defect at the level of the census itself
        # (whole-branch QA, HIGH-1).  They now go through `_coerce_str_map`.
        graph.schema = [
            SchemaField(
                # The owner carries the index: `campo ilegible: schema.key` cannot
                # be traced back to which entry produced it (Inc-1 review, F7).
                **_coerce_text_fields(graph, f"schema[{i}]", SchemaField, f),
                required=f.get("required", False),
            )
            for i, f in enumerate(sidecar.get("schema", []))
        ]
        documents: dict[str, Document] = {}
        for i, d in enumerate(sidecar.get("documents", [])):
            if not d.get("name"):
                continue
            doc = Document(
                **_coerce_text_fields(graph, f"document[{i}]", Document, d),
                **{
                    name: _coerce_str_map(
                        graph, f"document[{i}]", name, d.get(name, {})
                    )
                    for name in _str_map_fields(Document)
                },
                template=d.get("template", False),
            )
            if doc.name in documents:
                # NOTE THE FENCE.  This fires for a coercion-induced collision
                # (names `1` and `"1"`), which is `LLR-STO.1.1`'s business -- and
                # ALSO for two plainly identical names, where no coercion is
                # involved.  That second case was a silent overwrite before this
                # line and is a STRICT SUPERSET of what the requirement asked for.
                # Declared rather than left to be discovered (review G3).
                graph.load_warnings.append(
                    f"documento duplicado: {doc.name!r} <- {d.get('name')!r}"
                )
            documents[doc.name] = doc
        graph.documents = documents
        nodes_data = sidecar.get("nodes", {})
        seen_ids: set[str] = set()
        for raw_nid, ndata in nodes_data.items():
            # The node id is itself a text position: it is a dict KEY, so it never
            # passed through the field ladder.  Coercing it normalises the key TYPE
            # so `graph.nodes`, which is keyed by `str`, cannot be handed an int.
            #
            # It does NOT remove a phantom node: a sidecar id matching no parsed
            # node is still added alongside the parsed ones and still moves
            # `coverage()`'s denominator.  That is outside this batch's fence, and
            # saying otherwise here would be a false record in the evidence
            # (Inc-1 review, F4 -- the previous comment claimed the repair).
            # The raw id is in the label: two distinct refused ids both coerce to
            # `""` and previously emitted two byte-identical records, which is the
            # defect F7/G4 fixed everywhere EXCEPT here -- limb 2 of that fix never
            # landed (whole-branch QA, MEDIUM-4).
            nid = _coerce_field(graph, "node", f"id[{raw_nid!r}]", raw_nid)
            if nid in seen_ids:
                # Two raw ids coerced to one string; without this the second node's
                # ficha silently overwrites the first's.  The raw origin is carried
                # for the same reason as the field-key record above (review G2).
                graph.load_warnings.append(f"nodo duplicado: {nid!r} <- {raw_nid!r}")
            seen_ids.add(nid)
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
            # The KEY is a text position too, and it was raw: only the value went
            # through the ladder.  Built as a loop rather than a comprehension so a
            # collision can be recorded: two raw keys can coerce to one string (and
            # every refused key coerces to `""`), and keeping the last silently
            # deletes the first from the file on the next save (Inc-1 review, F3).
            coerced_fields: dict[str, str] = {}
            for key, value in raw_fields.items():
                # The label carries the raw key's `repr`: a refused key has no
                # faithful text form, so `str(key)` would claim one it does not
                # have, and the bare literal `"key"` cannot say which key (F7).
                ckey = _coerce_field(graph, nid, f"key[{key!r}]", key)
                if ckey in coerced_fields:
                    # Both coordinates AND the raw origin: a refused key coerces to
                    # `""`, so `{nid}.{ckey}` alone renders as `A.` and cannot say
                    # WHICH keys collided (review G2).
                    graph.load_warnings.append(
                        f"campo duplicado: {nid}.{ckey!r} <- {key!r}"
                    )
                coerced_fields[ckey] = _coerce_field(graph, nid, str(key), value)
            node.ficha = Ficha(
                **{
                    attr: _coerce_field(graph, nid, attr, ndata.get(attr, ""))
                    for attr in text_attrs
                },
                fields=coerced_fields,
                attachments=[
                    # `a["kind"]`/`a["path"]` were direct-indexed, so a sidecar
                    # missing either raised a bare `KeyError` out of `load` --
                    # S-11's family.  `_coerce_text_fields` defaults them instead.
                    #
                    # A non-mapping entry is REFUSED AND RECORDED by `_mappings`,
                    # never silently dropped: this is the same sink the `fields`
                    # guard above uses, and dropping it silently destroyed operator
                    # data on the next save (Inc-1 review, F1).
                    Attachment(**_coerce_text_fields(graph, f"{nid}.att[{i}]", Attachment, a))
                    for i, a in enumerate(
                        _mappings(graph, nid, "attachments", ndata.get("attachments", []))
                    )
                ],
            )
        return graph

    def load(self, map_id: str) -> Graph:
        mmd_path = self.workspace / f"{map_id}.mmd"
        yml_path = self.workspace / f"{map_id}_nodos.yml"
        if not mmd_path.exists():
            raise MapStoreError(f"Map not found: {mmd_path}")
        try:
            # These reads sat OUTSIDE every net, so invalid UTF-8 in either file
            # raised a bare `UnicodeDecodeError` straight out of `load`, and an
            # `OSError` carried its full absolute path -- username included --
            # into the operator-facing sink.  Threshold 3 said neither could
            # happen (security review F1/F3).
            mmd_text = mmd_path.read_text(encoding="utf-8")
            yml_text = (
                yml_path.read_text(encoding="utf-8") if yml_path.exists() else "{}"
            )
        except (OSError, UnicodeDecodeError) as exc:
            raise MapStoreError(
                f"no se pudo leer {map_id}: {type(exc).__name__}"
            ) from exc
        try:
            sidecar = yaml.safe_load(yml_text) or {}
        except (yaml.YAMLError, ValueError, RecursionError) as exc:
            # `ValueError` is not redundant beside `YAMLError`: PyYAML's own int
            # constructor calls `int(token)`, and CPython caps integer parsing at
            # `sys.get_int_max_str_digits()` (4300).  A sidecar field with more
            # digits than that raises a BARE ValueError from inside the parser —
            # before any field-level code runs — so the coercion ladder never
            # sees it and cannot defend against it.
            #
            # `RecursionError` is the same shape: PyYAML's scanner recurses per
            # nesting level, so a 4 KB sidecar nested ~2000 deep exhausts the
            # stack inside `safe_load`. Measured: depth 200 loads, depth 2000
            # raised a bare `RecursionError` out of `load` (security review F1).
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

        if not isinstance(sidecar, dict):
            # A top-level list or scalar reached `.get` and raised a bare
            # `AttributeError` out of `load`.  S-11's family.
            raise MapStoreError(
                f"no se pudo leer la ficha de {map_id}: {yml_path.name} ilegible"
            )
        try:
            graph = self._graph_from_sidecar(mmd_text, sidecar)
        except MermaidError as exc:
            raise MapStoreError(
                f"el mapa tiene un ciclo: {CYCLE_ARROW.join(exc.cycle)}"
            ) from exc
        except MapStoreError:
            raise
        except Exception as exc:  # noqa: BLE001
            # LLR-STO.1.1 threshold 3.  Measured at `d877784`, a container in a
            # sidecar text position raised `sqlite3.ProgrammingError` (x3) and
            # `TypeError` (x1) from here.
            #
            # WHAT THIS NET DOES, STATED HONESTLY.  An earlier version of this
            # comment said "every caller in the product catches `MapStoreError`".
            # That was FALSE: `grep -rn "except MapStoreError" mapper/` outside
            # this file returns nothing, and both real `load` callers
            # (`app.py:450`, `app.py:1179`) catch bare `Exception`.  So this net
            # does NOT prevent a crash at any existing call site -- it converts an
            # untyped escape into an operator-legible Spanish message.  That is a
            # real win and a much smaller claim than the one previously recorded
            # (security review F2).
            #
            # The masked type is carried in the message because there is no
            # logging facility in `mapper/` to recover it from, and both sinks
            # render `str(e)` only -- without it, a genuine code defect in
            # `_graph_from_sidecar` is permanently indistinguishable from a
            # malformed file.  The path is never interpolated; the type name is.
            raise MapStoreError(
                f"no se pudo leer la ficha de {map_id}: {yml_path.name} ilegible "
                f"({type(exc).__name__})"
            ) from exc
        try:
            self._reindex(map_id, mmd_text, yml_text, graph)
        except MapStoreError:
            raise
        except Exception as exc:  # noqa: BLE001
            # The exception's `str` is NOT interpolated: for `sqlite3` and `OSError`
            # it routinely carries a filesystem path, and this string is shown to
            # the operator.  The type name is diagnostic without leaking one, and
            # the full chain survives on `__cause__` (Inc-1 review, F8).
            raise MapStoreError(
                f"no se pudo indexar {map_id}: {type(exc).__name__}"
            ) from exc
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
