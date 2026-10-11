"""Inc-M1 (perf batch, Lane M) — LLR-PERF.2.1: `Graph` serves adjacency from a
strong-reference private cache.

The cache's validity token is `_adj_src is self.edges and len(self.edges) ==
_adj_len` (mapper/model.py): a strong reference to the edges list it was built
from, plus the length recorded at build time.  `id()` recycling after garbage
collection can never fake a hit — the token PINS the old list, so its address
cannot be reused while the cache lives.  `add_edge`'s in-place append is caught
by the `len` half; wholesale replacement (the `_remove_subtree` shape) by the
`is` half.  Soundness rests on the edge-mutation census guarded here: the only
post-construction writers of `Graph.edges` are `mapper/model.py` `add_edge`
(append) and `mapper/screens/map/editing.py`
`_remove_subtree` (wholesale assignment) — and no in-place form
(`edges[i]=`, slice, `del`, `+=`, `*=`, `.sort`, `.reverse`, `.clear`,
`.extend`, `.insert`, `.remove`, `.pop`) or alias (`x = <expr>.edges` then `x`
mutated) appears anywhere under `mapper/`.  The census is AST-derived over a
COPY of the package for the in-place arms (one planted mutation per form); the
alias form DOCUMENTS ITS LIMITS — aliasing through function arguments,
containers, or attributes on other objects is NOT detected.

RED transcripts: `.dev-flow/2026-10-10-perf-batch/evidence/m1-red.transcript`.
"""
from __future__ import annotations

import ast
import shutil
from pathlib import Path

import pytest

import mapper
from mapper.app import MapperApp
from mapper.model import Edge, Graph, Node
from mapper.views.outline import OutlineRenderer
from mapper.views.state import ViewState

from tests.test_draft_save import WIDE, _open

# --- graph builders (small, local — the capture script's builders belong to
# Inc-M2's file; these cover this increment's boundary catalog) ---------------


def _wide(n: int) -> Graph:
    """One root with n-1 children — E = n-1, every lookup is one cache line."""
    g = Graph()
    g.add_node(Node(id="n0"))
    for i in range(1, n):
        g.add_node(Node(id=f"n{i}"))
        g.add_edge(Edge("n0", f"n{i}"))
    return g


def _deep_chain(n: int) -> Graph:
    g = Graph()
    for i in range(n):
        g.add_node(Node(id=f"d{i}"))
        if i:
            g.add_edge(Edge(f"d{i-1}", f"d{i}"))
    return g


def _forest() -> Graph:
    """Three trees, two of them single parentless nodes — the LOW-10 shape."""
    g = Graph()
    for nid in ("t1", "t2", "t3", "a1", "b1", "b2"):
        g.add_node(Node(id=nid))
    g.add_edge(Edge("t1", "a1"))
    g.add_edge(Edge("t2", "b1"))
    g.add_edge(Edge("t2", "b2"))
    return g


def _multi_parent_dag() -> Graph:
    """`shared` has TWO parents — `parent_of` must return the FIRST in edge
    order, exactly what the old linear scan returned."""
    g = Graph()
    for nid in ("p1", "p2", "shared", "leaf"):
        g.add_node(Node(id=nid))
    g.add_edge(Edge("p1", "shared"))
    g.add_edge(Edge("p2", "shared"))
    g.add_edge(Edge("p1", "p2"))
    g.add_edge(Edge("shared", "leaf"))
    return g


def _ref_index(graph: Graph) -> tuple[dict[str, list[str]], dict[str, str]]:
    """The brute-force O(E) reference: one linear pass, children in edge-list
    order, parents FIRST-match — a transcription of the pre-cache loops."""
    children: dict[str, list[str]] = {}
    parents: dict[str, str] = {}
    for e in graph.edges:
        children.setdefault(e.parent_id, []).append(e.child_id)
        parents.setdefault(e.child_id, e.parent_id)
    return children, parents


def _assert_matches_reference(graph: Graph) -> None:
    children, parents = _ref_index(graph)
    ids = set(graph.nodes) | {e.parent_id for e in graph.edges} | {
        e.child_id for e in graph.edges
    }
    for nid in ids:
        assert graph.children_of(nid) == children.get(nid, []), (
            f"children_of({nid!r}) drifted from the linear-scan reference"
        )
        assert graph.parent_of(nid) == parents.get(nid), (
            f"parent_of({nid!r}) drifted from the linear-scan reference"
        )


# --- TC-M1 / AT: mutation-script equality (LLR-PERF.2.1) ----------------------


def test_cache_mutation_script_equality():
    """Cached answers equal the brute-force reference at every script step.

    The load-bearing stretch: TWO wholesale `edges` replacements back to back
    with NO lookup in between — and BOTH length-preserving, so the `len` half
    of the token cannot catch them; only the strong-reference `is` half can.
    The first replacement's list is freed when the second is assigned, and
    CPython may well allocate the second list at the very same address — a
    length-only key (`len` matches, `id` reused) would fake a hit and serve
    the STALE index, which is why M-M1b (drop the `is` check) reddens this
    node deterministically.
    """
    g = _wide(6000)
    g.children_of("n0")  # warm
    _assert_matches_reference(g)

    n = 6000
    m = n - 1  # == len(g.edges): the replacements preserve length on purpose
    g.edges = [Edge(f"n{i}", f"n{(i + 1) % n}") for i in range(m)]  # replace 1
    g.edges = [Edge(f"n{i}", f"n{(i + 7) % n}") for i in range(m)]  # replace 2,
    # NO lookup in between: replacement 1's list is freed and its id may be
    # reused by replacement 2 — identity, not id, must carry validity.
    _assert_matches_reference(g)

    g.add_edge(Edge("n5999", "n0"))  # in-place append: the len half trips
    _assert_matches_reference(g)

    sub = g.focus("n10")  # a fresh Graph riding the same code
    _assert_matches_reference(sub)

    # Fresh-list semantics: a caller may bind the returned list and mutate it
    # (painting.py does) without poisoning the next call.
    bound = g.children_of("n5999")
    bound.append("junk-id")
    again = g.children_of("n5999")
    assert "junk-id" not in again, (
        "children_of returned the CACHED list itself — caller mutation leaks "
        "into the next lookup"
    )
    assert again == _ref_index(g)[0].get("n5999", [])

    # The boundary catalog's remaining shapes: forest, multi-parent DAG
    # (first-match), empty, deep chain 5000.
    dag = _multi_parent_dag()
    assert dag.parent_of("shared") == "p1", (
        "parent_of must keep first-match semantics on a multi-parent graph"
    )
    for graph in (_forest(), dag, Graph(), _deep_chain(5000)):
        graph.children_of("anybody")  # warm (also the empty-map arm)
        _assert_matches_reference(graph)
    assert Graph().children_of("n") == [] and Graph().parent_of("n") is None


# --- TC-M2: counted ops (LLR-PERF.2.1) ----------------------------------------


def test_cache_counted_ops():
    """After warm-up, 500 mixed lookups cost at most ONE full scan of `edges`.

    A counting wrapper replaces `graph.edges` wholesale (itself a legitimate
    invalidation: the first post-swap lookup rebuilds, every later one hits).
    The uncached baseline is 500 full scans; the cache must total ≤ 1.
    """
    g = _wide(1000)
    g.children_of("n0")  # warm

    class _CountingEdges(list):
        def __iter__(self):
            for edge in super().__iter__():
                self.visits += 1
                yield edge

    g.edges = _CountingEdges(g.edges)
    g.edges.visits = 0
    ids = [f"n{i}" for i in range(0, 1000, 10)]
    for i, nid in enumerate(ids * 5):  # 500 mixed lookups
        if i % 2:
            g.children_of(nid)
        else:
            g.parent_of(nid)
    assert g.edges.visits > 0, "the counting wrapper observed no edge visits"
    assert g.edges.visits <= len(g.edges), (
        f"cache bypassed: {g.edges.visits} edge visits for 500 warmed lookups "
        f"on E={len(g.edges)} (a single full scan is the whole budget)"
    )


# --- TC-M3: the edge-mutation census guard (LLR-PERF.2.1 soundness basis) -----

# The declared post-construction writer sites of `Graph.edges` — the census
# this batch relied on at P1 (requirement row 4), pinned mechanically.
_DECLARED_WRITERS = {
    ("model.py", "Graph.add_edge"),  # append, mapper/model.py
    ("screens/map/editing.py", "EditingOps._remove_subtree"),  # wholesale assign
}

# In-place forms the guard flags, one planted mutation per parametrized arm.
_CENSUS_MUTATIONS = {
    "setitem": "def _m(g):\n    g.edges[0] = None\n",
    "slice": "def _m(g):\n    g.edges[0:1] = []\n",
    "del": "def _m(g):\n    del g.edges[0]\n",
    "iadd": "def _m(g):\n    g.edges += []\n",
    "imul": "def _m(g):\n    g.edges *= 1\n",
    "sort": "def _m(g):\n    g.edges.sort()\n",
    "reverse": "def _m(g):\n    g.edges.reverse()\n",
    "clear": "def _m(g):\n    g.edges.clear()\n",
    "extend": "def _m(g):\n    g.edges.extend([])\n",
    "insert": "def _m(g):\n    g.edges.insert(0, None)\n",
    "remove": "def _m(g):\n    g.edges.remove(None)\n",
    "pop": "def _m(g):\n    g.edges.pop()\n",
    # ALIAS — DOCUMENTED LIMITS (ruling R18): only `x = <expr>.edges` with `x`
    # then mutated in the SAME scope is detected; aliasing through function
    # arguments, containers, or attributes on other objects is NOT detected.
    "alias": "def _m(g):\n    x = g.edges\n    x.append(None)\n",
}

_MUTATING_METHODS = {"append", "extend", "insert", "remove", "pop", "sort",
                     "reverse", "clear"}


def _is_edges_attr(node: ast.AST) -> bool:
    return isinstance(node, ast.Attribute) and node.attr == "edges"


def _edges_census(root: Path) -> tuple[set[tuple[str, str]], list[str]]:
    """AST-derived census of `edges` writers under `root` (the package dir).

    Returns `(writers, violations)`: every writer site as (relative path,
    qualified name), and every violation as `form at path:qual`.  A writer is
    only legal at the two declared sites; every in-place form and alias is a
    violation anywhere.
    """
    writers: set[tuple[str, str]] = set()
    violations: list[str] = []

    def scan(rel: str, tree: ast.AST) -> None:
        # Pass A: alias names per scope (`x = <expr>.edges`).  Per-scope, not
        # flow-sensitive — the documented limit above.
        aliases: dict[str, set[str]] = {}

        def collect_aliases(qual: str, node: ast.AST) -> None:
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    collect_aliases(f"{qual}{child.name}.", child)
                elif isinstance(child, ast.Assign) and _is_edges_attr(child.value):
                    for t in child.targets:
                        if isinstance(t, ast.Name):
                            aliases.setdefault(qual, set()).add(t.id)

        collect_aliases("", tree)

        # Pass B: writers and in-place forms.
        def visit(qual: str, node: ast.AST) -> None:
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    visit(f"{qual}{child.name}.", child)
                    continue
                scope_aliases = aliases.get(qual, set())
                site = f"{rel}:{qual.rstrip('.') or '<module>'}"
                if isinstance(child, ast.Assign):
                    for t in child.targets:
                        if _is_edges_attr(t):
                            writers.add((rel, qual.rstrip(".") or "<module>"))
                            if (rel, qual.rstrip(".") or "<module>") not in _DECLARED_WRITERS:
                                violations.append(f"assign at {site}")
                elif isinstance(child, ast.AnnAssign) and _is_edges_attr(child.target):
                    writers.add((rel, qual.rstrip(".") or "<module>"))
                    if (rel, qual.rstrip(".") or "<module>") not in _DECLARED_WRITERS:
                        violations.append(f"assign at {site}")
                elif isinstance(child, ast.AugAssign):
                    if _is_edges_attr(child.target):
                        form = "iadd" if isinstance(child.op, ast.Add) else (
                            "imul" if isinstance(child.op, ast.Mult) else "aug"
                        )
                        violations.append(f"{form} at {site}")
                    elif isinstance(child.target, ast.Name) and child.target.id in scope_aliases:
                        violations.append(f"alias at {site}")
                elif isinstance(child, ast.Delete):
                    for t in child.targets:
                        if _is_edges_attr(t) or (
                            isinstance(t, ast.Subscript) and _is_edges_attr(t.value)
                        ):
                            violations.append(f"del at {site}")
                        elif isinstance(t, ast.Name) and t.id in scope_aliases:
                            violations.append(f"alias at {site}")
                elif isinstance(child, ast.Subscript) and isinstance(child.ctx, ast.Store):
                    if _is_edges_attr(child.value):
                        form = "slice" if isinstance(child.slice, ast.Slice) else "setitem"
                        violations.append(f"{form} at {site}")
                    elif isinstance(child.value, ast.Name) and child.value.id in scope_aliases:
                        violations.append(f"alias at {site}")
                elif isinstance(child, ast.Call):
                    f = child.func
                    if isinstance(f, ast.Attribute) and f.attr in _MUTATING_METHODS:
                        if _is_edges_attr(f.value):
                            w = (rel, qual.rstrip(".") or "<module>")
                            writers.add(w)
                            if w not in _DECLARED_WRITERS:
                                violations.append(f"{f.attr} at {site}")
                        elif isinstance(f.value, ast.Name) and f.value.id in scope_aliases:
                            violations.append(f"alias at {site}")
                visit(qual, child)

        visit("", tree)

    for path in sorted(root.rglob("*.py")):
        rel = path.relative_to(root).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        scan(rel, tree)
    return writers, violations


def _mapper_pkg_dir() -> Path:
    return Path(mapper.__file__).parent


def test_edges_writer_census():
    """The guard's baseline: writers == the declared set, zero violations.

    Asserts BOTH directions: a new writer site (M-M1c) reddens the equality,
    and a removed writer reddens it too — an emptied census cannot pass
    vacuously.
    """
    writers, violations = _edges_census(_mapper_pkg_dir())
    assert writers == _DECLARED_WRITERS, (
        f"the edges-writer census drifted: {writers} != {_DECLARED_WRITERS}"
    )
    assert violations == [], f"in-place edges mutation found: {violations}"


@pytest.mark.parametrize("form", sorted(_CENSUS_MUTATIONS))
def test_census_in_place_forms(tmp_path, form):
    """One planted in-place form per arm (M-M1c) — the guard must flag it.

    The mutation is planted in a TMP COPY of the package; the product tree is
    never touched.  Each snippet is a function body so the planted module
    still imports.
    """
    copy = tmp_path / "mapper"
    shutil.copytree(_mapper_pkg_dir(), copy)
    with (copy / "model.py").open("a", encoding="utf-8") as fh:
        fh.write("\n\n" + _CENSUS_MUTATIONS[form])
    _, violations = _edges_census(copy)
    assert any(v.startswith(f"{form} at ") for v in violations), (
        f"planted {form!r} mutation was NOT flagged: {violations}"
    )


# --- TC-M5 (code-review follow-up, Inc-M1): mid-rebuild failure ---------------
# `m1b-red.transcript` — token-last ordering is the commit point.


def test_mid_rebuild_failure_leaves_token_invalid(monkeypatch):
    """A crash between the index build and the token must not publish a token
    valid against a stale index (code-review finding on `_adjacency`:
    the old code assigned `_adj_src`/`_adj_len` BEFORE `_adj_children`/
    `_adj_parents`).

    A one-shot descriptor on `Graph._adj_children` raises from `__set__` the
    first time the rebuilt index is stored — landing BETWEEN the old token
    assignment and the old index assignment.  Caught, the next lookup must
    recompute cleanly: under the OLD ordering the token was already committed,
    so the next call hit the STALE warm-up index and served pre-mutation
    answers (this node is RED there — `m1b-red.transcript`); under the fixed
    ordering the token is assigned LAST, so the failed rebuild left the cache
    invalid and the next lookup rebuilds.
    """
    g = _wide(10)
    g.children_of("n0")  # warm: token valid, index holds the 9-edge graph
    g.add_edge(Edge("n3", "n4"))  # mutation: the token goes stale

    class _FailOnce:
        def __init__(self):
            self._armed = True

        def __get__(self, obj, objtype=None):
            if obj is None:
                return self
            return obj.__dict__["_adj_children"]

        def __set__(self, obj, value):
            if self._armed:
                self._armed = False
                raise RuntimeError("simulated crash mid-rebuild")
            obj.__dict__["_adj_children"] = value

    # The class attribute does not exist (default_factory field), so
    # `raising=False`; monkeypatch deletes it again on teardown.
    monkeypatch.setattr(Graph, "_adj_children", _FailOnce(), raising=False)
    with pytest.raises(RuntimeError, match="simulated crash mid-rebuild"):
        g.children_of("n4")  # miss → rebuild → the one-shot crash fires
    _assert_matches_reference(g)  # next lookup recomputes from scratch


# --- TC-M4: LOW-10 — minimap/outline bytes byte-stable across the cache -------


async def test_minimap_outline_forest_dag_bytes(tmp_path):
    """Minimap and outline painted bytes over a forest (opened in the real app)
    and a multi-parent DAG (built directly — never loadable), byte-stable
    across cache warm-up and a wholesale `edges` replacement.

    A fresh uncached copy of each graph must paint identical bytes, so a
    cache-order drift reddens this node while leaving the reference render
    untouched.
    """
    forest = _forest()
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        app.store.save("f", forest)
        screen = await _open(app, pilot, "f", cursor="t1")

        mm_w = 40
        minimap_before = screen._minimap_text(mm_w).plain
        outline_before = OutlineRenderer().render(
            forest, ViewState(selected_id="t1", w=80, h=24)
        ).plain
        # Warm the cache the way navigation does, then look up every node.
        await pilot.press("j")
        for nid in forest.nodes:
            forest.children_of(nid)
            forest.parent_of(nid)
        # The _remove_subtree shape: wholesale replacement, same content.
        forest.edges = [e for e in forest.edges]
        assert screen._minimap_text(mm_w).plain == minimap_before, (
            "minimap bytes drifted across the cache"
        )
        assert OutlineRenderer().render(
            forest, ViewState(selected_id="t1", w=80, h=24)
        ).plain == outline_before, "outline bytes drifted across the cache"

        # Multi-parent DAG, built directly and installed on the screen (it can
        # never be saved and re-opened — the parser refuses multi-parent).
        dag = _multi_parent_dag()
        screen.graph = dag
        dag_minimap = screen._minimap_text(mm_w).plain
        dag_outline = OutlineRenderer().render(
            dag, ViewState(selected_id="p1", w=80, h=24)
        ).plain
        for nid in dag.nodes:
            dag.children_of(nid)
            dag.parent_of(nid)
        dag.edges = [e for e in dag.edges]
        assert screen._minimap_text(mm_w).plain == dag_minimap
        assert OutlineRenderer().render(
            dag, ViewState(selected_id="p1", w=80, h=24)
        ).plain == dag_outline

        # Uncached fresh copies paint identical bytes (the order oracle).
        assert OutlineRenderer().render(
            _multi_parent_dag(), ViewState(selected_id="p1", w=80, h=24)
        ).plain == dag_outline
    fresh = _forest()
    assert OutlineRenderer().render(
        fresh, ViewState(selected_id="t1", w=80, h=24)
    ).plain == outline_before
