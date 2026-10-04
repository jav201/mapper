"""The Inc-4a fixture (`QA-N-08`), GENERATED — never a file under `fixtures/`.

Not a test module (no `test_` prefix, so pytest does not collect it).

WHY GENERATED AND NOT SHIPPED.  It is not a style preference and the cost was
paid once already: a probe that pointed the app at the real `fixtures/`
directory had the inspector's commit-on-blur write through and permanently
altered tracked fixture files.  A fixture that has no tracked file cannot have
one altered.  The pair is written into a `tmp_path` workspace and loaded through
the real `MapStore.load`, the same load path `inc3_support.install` exercises —
so the fixture still travels the shipped parser, the shipped coercion and the
shipped attachment sidecar, and only its CONTENT is synthetic.

WHY THE SHIPPED FIXTURES CANNOT SERVE.  Executed on `legacy` at `5f4816c`:
**0 attachments**, and 4 of its 8 nodes carry no `meta` at all.  `LLR-N07.1.2`'s
widening has three arms — id, subtitle (`Ficha.meta`) and attachment — and two
of the three are undrivable on any fixture that exists.  `legacy` is also
vacuous for `LLR-N07.3.1`'s tree-order self-guard: under BOTH of the batch's
working queries (`carlos`, `riesgo`) its hits come out with
`tree_order == dict_order`, so a tree-order assertion written against it would
have passed while asserting nothing.

WHAT EACH NODE IS FOR — every one is load-bearing, none is decoration:

    id            title                 matches `riesgo` by   old predicate?
    riesgo-root   Cartera               id only               no
    b             Contratos en riesgo   title                 yes  (control)
    c             Auditoria             meta / subtitle only  no
    d             Proveedores           field value           yes  (control)
    e             Seguros               attachment caption    no
    f             Hallazgos             — (non-hit)           no

`f` and the second foldable branch `c` are the two that look like padding and
are not.  Without `c -> f` the "b's pill is gone" predicate degenerates into
"the canvas contains zero fold pills", which is green on an implementation whose
pill layer stopped painting entirely; with it, the same predicate asserts b's
pill is gone AND c's pill is still there.  Without `f` there is no node for
"paints no node with the hit style" to be false about.
"""
from __future__ import annotations

from mapper.model import Graph
from mapper.store import MapStore

MAP_ID = "adjuntos"

# The pinned query, and the ONE place it is spelled.  Every predicate reads it
# from here so a fixture edit and an expectation edit cannot drift apart.
QUERY = "riesgo"

# A query that matches nothing in this graph.  Any absent token serves; it is
# pinned so the artifact is reproducible.
ABSENT_QUERY = "zzzz"

_MMD = """graph TD
    riesgo-root[Cartera]
    riesgo-root --> b[Contratos en riesgo]
    riesgo-root --> c[Auditoria]
    b --> d[Proveedores]
    b --> e[Seguros]
    c --> f[Hallazgos]
"""

_YML = """schema:
  - key: E
    label: estado
    required: false

nodes:
  riesgo-root:
    title: Cartera
    state: ''
    meta: vigente
    notes: ''
    fields: {}
    attachments: []
  b:
    title: Contratos en riesgo
    state: ''
    meta: cartera activa
    notes: ''
    fields:
      E: abierto
    attachments: []
  c:
    title: Auditoria
    state: ''
    meta: riesgo alto
    notes: ''
    fields: {}
    attachments: []
  d:
    title: Proveedores
    state: ''
    meta: cadena externa
    notes: ''
    fields:
      E: riesgo
    attachments: []
  e:
    title: Seguros
    state: ''
    meta: poliza vigente
    notes: ''
    fields: {}
    attachments:
      - kind: file
        path: docs/poliza.pdf
        caption: informe de riesgo 2026
  f:
    title: Hallazgos
    state: ''
    meta: cierre anual
    notes: ''
    fields: {}
    attachments: []
"""


def build_adjuntos(tmp_path) -> Graph:
    """Write the `.mmd` + `_nodos.yml` pair into *tmp_path* and load it."""
    (tmp_path / f"{MAP_ID}.mmd").write_text(_MMD, encoding="utf-8")
    (tmp_path / f"{MAP_ID}_nodos.yml").write_text(_YML, encoding="utf-8")
    return MapStore(tmp_path).load(MAP_ID)


def narrow_hits(graph: Graph, query: str) -> list[str]:
    """The renderer's OLD inline predicate, reproduced here as a control.

    Written out rather than imported, deliberately: `LLR-N07.1.1` deletes the
    production copy, and a control imported from the thing under test would be
    deleted along with it — leaving an arm that reads like a negative control
    and asserts nothing.  Three haystacks (title, notes, field values) against
    `Graph.search_hits`' six; the delta is exactly `{id, meta, attachments}`.
    """
    q = query.lower()
    if not q:
        return []
    out = []
    for node in graph.nodes.values():
        if (
            q in node.ficha.title.lower()
            or q in node.ficha.notes.lower()
            or any(q in v.lower() for v in node.ficha.fields.values())
        ):
            out.append(node.id)
    return out


def child_index(graph: Graph) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for edge in graph.edges:
        index.setdefault(edge.parent_id, []).append(edge.child_id)
    return index


def descendants_of(graph: Graph, nid: str) -> frozenset[str]:
    """The oracle's OWN descendant walk, so no predicate asks the product."""
    index = child_index(graph)
    out: set[str] = set()
    stack = list(index.get(nid, ()))
    while stack:
        cid = stack.pop()
        if cid in out:
            continue
        out.add(cid)
        stack.extend(index.get(cid, ()))
    return frozenset(out)


def expected_tree_order(graph: Graph) -> list[str]:
    """Pre-order DFS the test writes ITSELF, never asking `mapper.search`.

    An ordering assertion that obtains its expectation from the ordering helper
    asserts that the helper agrees with itself.
    """
    out: list[str] = []
    if graph.root_id is None:
        return out
    index = child_index(graph)
    seen: set[str] = set()
    stack = [graph.root_id]
    while stack:
        nid = stack.pop()
        if nid in seen or nid not in graph.nodes:
            continue
        seen.add(nid)
        out.append(nid)
        for cid in reversed(index.get(nid, ())):
            if cid not in seen:
                stack.append(cid)
    return out
