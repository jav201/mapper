"""HLR-R02 — a deep map draws, or says why not; it never raises RecursionError.

S-01b: a depth-500 *acyclic* chain — a perfectly legitimate map — raised
`RecursionError` in 0.01 s at `mapper/views/radial.py:24 _leaves`.  Cycle
refusal (HLR-R01, increment 1) does not touch this: the graph here is valid and
merely deep.

**Why the fixture is 5000 levels and not 500.**  The plausible-weaker arm
declared for `AT-R04` is `sys.setrecursionlimit` — raise the limit instead of
removing the recursion.  At depth 500 that arm is green, so a depth-500 fixture
cannot discriminate a fix from a limit-raise.  Measured on this interpreter
(CPython 3.12.7): the shipped `sum(genexpr)` recursion shape stops at depth
**1499** *under `sys.setrecursionlimit(1_000_000)`* — that is CPython's separate
C-recursion ceiling, which no recursion limit lifts.  5000 is past it, so no
limit-raise can rescue `_leaves`.  For the plain Python-to-Python recursions
(`layered.walk`, `outline.walk`, `radial.place`) a large enough limit *would*
survive 5000, so those are pinned from the other side instead: the limit test
below *lowers* the limit while rendering, an arm that raises it cannot pass.
"""
from __future__ import annotations

import ast
import hashlib
import inspect
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
from rich.markup import escape
from rich.text import Text

import mapper
from mapper import darkside
from mapper.app import MapperApp, MapScreen
from mapper.mermaid import parse
from mapper.model import Document, Edge, Ficha, Graph, Node
from mapper.views.state import ViewState
from mapper.screens.factory import FactoryScreen
from mapper.store import MapStore
from mapper.views import LayeredRenderer, OutlineRenderer, RadialRenderer
from mapper.views import layered as layered_mod
from mapper.views import outline as outline_mod
from mapper.views import radial as radial_mod
from mapper.widgets.rail import RAIL_WIDTH, OutlineRail

MAPPER_DIR = Path(mapper.__file__).parent
REPO_ROOT = MAPPER_DIR.parent
VIEWS_DIR = Path(radial_mod.__file__).parent
FIXTURES = REPO_ROOT / "fixtures"

DEEP = 5000
"""See the module docstring: past the measured 1499-frame C-recursion ceiling."""

RENDERERS = (
    ("radial", RadialRenderer),
    ("layered", LayeredRenderer),
    ("outline", OutlineRenderer),
)

# AT-R05's declared bound.  Measured here at 140x45, worst of five repeats over
# a 3000-node balanced tree: radial 0.0885 s, layered 0.0416 s, outline 0.0253 s.
# The worst render anywhere at or under MAX_RENDER_NODES was 0.2899 s.  The
# declared bound is ~7x that worst case, which is headroom for a loaded machine
# and still far below the quadratic behaviour this increment removed.
RENDER_BOUND_SECONDS = 2.0

# The factory tree gets its own, larger bound, and the reason is not slack.
# `_tree_lines` emits the FULL indent — that indent IS the picture, so unlike
# the rail it cannot be capped without changing what it draws.  At depth 5000
# its output is 25,043,898 characters, so it is quadratic in characters by
# construction.  Worst of five repeats at depth 5000: 2.2472 s; best 1.3549 s;
# one run at 2.236 s reddened a 2.0 s bound on a loaded machine, which is what
# put this constant here.  The bound is ~3.6x the worst measurement.  This cost
# belongs to the SHAPE OF THE OUTPUT, not to how the traversal walks — the walk
# itself is pinned by the scan counts below, which no machine load can move.
FACTORY_TREE_BOUND_SECONDS = 8.0

# C-53's false-failure arm.  sha256 over (plain text, style spans) of each
# renderer's output for fixtures/legacy.mmd with "fin" selected, captured from
# the implementations on `master`.  A depth fix that changes ordinary output is
# a regression, so these are pinned.
#
# Increment 2 pinned ONE terminal size, 140x45, while the change it was pricing
# — layered.py's body_h cap — is a function of h (increment 2 review, finding
# F4).  The sizes below are four, chosen so that h is short, ordinary and long,
# and w is narrow, ordinary and wide.  The three 140x45 digests are byte-equal
# to the three increment 2 pinned, which is what says the capture method here
# reproduces the one that produced them.
GOLDEN_SIZES = ((140, 45), (80, 24), (140, 8), (300, 120))

MASTER_LEGACY_DIGESTS = {
    ("LayeredRenderer", 140, 45): "a76157aa1fe1c5da5cfc6dfc1ede7bf32b0a06b41245476840664cea7ee09ca9",
    ("LayeredRenderer", 80, 24): "5a519c0c42a831f2d23ba4074932787a413db2c0d3648d3f9cae6c9d432c0aec",
    ("LayeredRenderer", 140, 8): "8383658991105a00895d489bfcc3aa709bc66f444d00a34e1b605e0114e0c976",
    ("LayeredRenderer", 300, 120): "e133509b464d85d5d34256468c9832abc014699ab581283ae91ee939779bd320",
    ("OutlineRenderer", 140, 45): "2d71af9ac6817c2441d152ba2fb1758e9b75789ce2bac2975fd1cff5f980d201",
    ("OutlineRenderer", 80, 24): "2d71af9ac6817c2441d152ba2fb1758e9b75789ce2bac2975fd1cff5f980d201",
    ("OutlineRenderer", 140, 8): "5ec6a1051d11fbbb213efadc4f7efafa5487512cbd9fd597b971b4b0b24a022f",
    ("OutlineRenderer", 300, 120): "2d71af9ac6817c2441d152ba2fb1758e9b75789ce2bac2975fd1cff5f980d201",
    # The four RadialRenderer keys below were RE-BASELINED in
    # 2026-08-26-ui-next-batch-02 Inc-1, and the move is CORRECT behaviour, not
    # a regression: `Canvas.rows()` now composes the `dots` and `bgs` layers it
    # used to discard, and RadialRenderer is the only renderer in the tree that
    # writes them (measured: exactly two `.dots` sites, both in radial.py;
    # LayeredRenderer's dots are 0 and OutlineRenderer builds no Canvas).  The
    # predicted-red set was derived BEFORE the change and matched exactly: all
    # four Radial keys moved, all eight Layered/Outline keys held byte-identical
    # and were NOT recaptured.  Re-capturing a predicted-green digest is a gate
    # failure, because it silently drops the guard on a renderer that must not
    # move -- which is what a wholesale re-capture of this dictionary does.
    ("RadialRenderer", 140, 45): "398b922562e3b3b7809296b0afb7b5ba3785371b7f11e6992e6a5b6e78d13d99",
    ("RadialRenderer", 80, 24): "3f174032180edeab8e3a362a19608eaa060680e623912f46834a73921c46e5df",
    ("RadialRenderer", 140, 8): "4dee6c1c4fcd527b32b508bbb22f171b5026de09a0bf2b39729bf2a0794f08d0",
    ("RadialRenderer", 300, 120): "3f8dac90f262d9cba30138c43a15d30f48b0218049cdb43834128a77073f5337",
}

# The same arm for this increment's two files.  `OutlineRail.render` takes no
# size — RAIL_WIDTH is fixed — so the input most likely to expose a memo keyed
# wrongly is `collapsed`, and that is what is varied here.  Captured from
# `rail.py` and `factory.py` as they stand on `master`; both were byte-identical
# to `master` in the tree this increment started from.
MASTER_RAIL_DIGESTS = {
    (): "cf3cddd273ec0ef1418fca99eed2108a796a81d4fc420d57d56d602f232d8443",
    ("fin",): "7e237f6166867a067445bc949929be884c8c9ab0ffdf5f8a8ec7ac505e399e8d",
    ("fin", "rrhh"): "ab0d3e14a91e325a9d6ddce91dcde03762cbe60a450e6d17ae6a49efcb68e8ae",
    ("erp",): "b528ab941f62298182159152a653eccfbe4437c87fc0b0a365185c4c6f7517d6",
    ("inv", "fin", "rrhh"): "58d9452cf3c00361e4f1d7b334c570173029471e1281c85af336978e681f7283",
}

MASTER_FACTORY_TREE_DIGEST = (
    "9ffadc425a42d976af8a0898e7967b71e8e839e4bb60c44bd4a6e3880dff9af4"
)

# Spanish UI fragments, built from code points so this file stays ASCII and a
# mangled accent cannot pass unnoticed (same discipline as test_repair_cycles).
OMITTED = "Se omiti" + chr(0xF3)          # "Se omitió"
OVER_BOUND = "supera el l" + chr(0xED) + "mite"   # "supera el límite"
CYCLE_NOTICE = "el mapa tiene un ciclo"
GUARD_MESSAGE = "cycle through"


# --------------------------------------------------------------------------
# graph builders


def _chain(depth: int) -> Graph:
    graph = Graph()
    for i in range(depth + 1):
        graph.add_node(Node(id=f"n{i}", ficha=Ficha(title=f"N{i}")))
    for i in range(depth):
        graph.add_edge(Edge(parent_id=f"n{i}", child_id=f"n{i + 1}"))
    return graph


def _balanced(n: int, fan: int = 8) -> Graph:
    graph = Graph()
    ids = [f"n{i}" for i in range(n)]
    for nid in ids:
        graph.add_node(Node(id=nid, ficha=Ficha(title=nid)))
    for i in range(1, n):
        graph.add_edge(Edge(parent_id=ids[(i - 1) // fan], child_id=ids[i]))
    return graph


def _from_pairs(root: str, pairs: list[tuple[str, str]]) -> Graph:
    graph = Graph()
    graph.add_node(Node(id=root, ficha=Ficha(title=root)))
    for parent, child in pairs:
        for nid in (parent, child):
            if nid not in graph.nodes:
                graph.add_node(Node(id=nid, ficha=Ficha(title=nid)))
        graph.add_edge(Edge(parent_id=parent, child_id=child))
    return graph


def _legacy_graph(tmp_path) -> Graph:
    for name in ("legacy.mmd", "legacy_nodos.yml"):
        (tmp_path / name).write_text(
            (FIXTURES / name).read_text(encoding="utf-8"), encoding="utf-8"
        )
    return MapStore(tmp_path).load("legacy")


def _deep_chain_source(depth: int) -> str:
    nl = chr(10)
    body = "".join(f"  n{i}[N{i}] --> n{i + 1}[N{i + 1}]{nl}" for i in range(depth))
    return f"graph TD{nl}{body}"


def _fingerprint(text) -> str:
    payload = repr((text.plain, [(s.start, s.end, str(s.style)) for s in text.spans]))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _stack_depth() -> int:
    depth, frame = 0, sys._getframe()
    while frame is not None:
        depth += 1
        frame = frame.f_back
    return depth


def _peak_call_depth(call):
    """Run `call` under a profile hook and report its deepest Python nesting.

    This is the oracle no recursion-limit trick can dodge.  Pinning
    `sys.setrecursionlimit` low is defeated by an implementation that raises the
    limit again from inside `render`; counting frames is not, because it asks
    the question the requirement actually asks — how deep does this traversal
    go — instead of asking what the interpreter is currently willing to tolerate.
    """
    depth = peak = 0

    def probe(frame, event, arg):
        nonlocal depth, peak
        if event == "call":
            depth += 1
            if depth > peak:
                peak = depth
        elif event == "return":
            depth -= 1

    sys.setprofile(probe)
    try:
        result = call()
    finally:
        sys.setprofile(None)
    return result, peak


# --------------------------------------------------------------------------
# LLR-R02.1 — the traversal set is derived, never hand-listed


# Increment 2's scanner flagged a function only when its own call names met
# `enclosing + [own name]`.  That predicate sees self-recursion and nothing
# else: a mutually recursive pair and a call through a module-level alias both
# measured `[]` against it (Increment 2 review, finding F3).  The engine below
# builds a call graph per module instead and reports every function that lies
# on a call CYCLE OF ANY LENGTH, so those two shapes fall out of the same rule.
#
# `super().__init__()` is excluded deliberately, not for convenience.  A
# `super()` call targets the parent class by definition, so it can never be a
# self-call; without the exclusion the scan reports 30 false positives across
# `widgets/` and `screens/` — every `__init__` that chains to its base.  A rule
# that false-fails correct work gets routed around, which is the C-53 failure
# mode applied to a probe rather than to a gate.


def _call_names(fn: ast.AST) -> set[str]:
    """Names called from `fn`'s OWN body, not from a function nested in it.

    Nested bodies are excluded so that an enclosing function does not inherit
    its closure's calls; the closure is a node of the call graph in its own
    right, and a real enclosing-to-nested cycle is found as a two-step cycle.
    """
    names: set[str] = set()
    pending = list(ast.iter_child_nodes(fn))
    while pending:
        node = pending.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            continue
        if isinstance(node, ast.Call):
            target = node.func
            if isinstance(target, ast.Name):
                names.add(target.id)
            elif isinstance(target, ast.Attribute):
                base = target.value
                chained_to_base_class = (
                    isinstance(base, ast.Call)
                    and isinstance(base.func, ast.Name)
                    and base.func.id == "super"
                )
                if not chained_to_base_class:
                    names.add(target.attr)
        pending.extend(ast.iter_child_nodes(node))
    return names


def _referenced_names(fn: ast.AST) -> set[str]:
    """Every plain and attribute name appearing anywhere inside `fn`."""
    names: set[str] = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.Name):
            names.add(node.id)
    return names


def _collect(node, scope, defs, aliases) -> None:
    """Index every def by qualname, plus module-level `x = y` alias pairs."""
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            qual = ".".join(scope + [child.name])
            defs[qual] = (tuple(scope), child.name, _call_names(child),
                          _referenced_names(child), child.lineno)
            _collect(child, scope + [child.name], defs, aliases)
        elif isinstance(child, ast.ClassDef):
            _collect(child, scope + [child.name], defs, aliases)
        else:
            if isinstance(child, ast.Assign) and isinstance(child.value, ast.Name):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        # Both directions: an alias makes the two names one
                        # callable, and either may be the one that is called.
                        aliases.setdefault(child.value.id, set()).add(target.id)
                        aliases.setdefault(target.id, set()).add(child.value.id)
            _collect(child, scope, defs, aliases)


def _resolve(name: str, scope: tuple, defs: dict) -> str | None:
    """The nearest def called `name` visible from `scope`, innermost first."""
    best = None
    for qual, (dscope, dname, _, _, _) in defs.items():
        if dname != name or list(dscope) != list(scope)[: len(dscope)]:
            continue
        if best is None or len(defs[best][0]) < len(dscope):
            best = qual
    return best


def _on_a_cycle(edges: dict[str, set[str]]) -> set[str]:
    """Every node that can reach itself — a cycle of any length, not just 1."""
    found: set[str] = set()
    for start in edges:
        seen: set[str] = set()
        pending = [start]
        while pending:
            current = pending.pop()
            for nxt in edges.get(current, ()):
                if nxt == start:
                    found.add(start)
                    pending = []
                    break
                if nxt not in seen:
                    seen.add(nxt)
                    pending.append(nxt)
    return found


def _recursive_defs(source: str) -> dict[str, tuple]:
    """{qualname: (lineno, names it or an enclosing def references)} on a cycle."""
    defs: dict[str, tuple] = {}
    aliases: dict[str, set[str]] = {}
    _collect(ast.parse(source), [], defs, aliases)

    edges: dict[str, set[str]] = {qual: set() for qual in defs}
    for qual, (dscope, dname, calls, _, _) in defs.items():
        reachable = set(calls)
        for called in calls:
            reachable |= aliases.get(called, set())
        for name in reachable:
            target = _resolve(name, tuple(list(dscope) + [dname]), defs)
            if target is not None:
                edges[qual].add(target)

    out: dict[str, tuple] = {}
    for qual in _on_a_cycle(edges):
        dscope, _, _, referenced, lineno = defs[qual]
        names = set(referenced)
        # A closure can inherit its adjacency index from the enclosing scope,
        # so the enclosing bodies count as part of what this def touches.
        for other, (oscope, oname, _, oreferenced, _) in defs.items():
            if list(oscope) + [oname] == list(dscope)[: len(oscope) + 1]:
                names |= oreferenced
        out[qual] = (lineno, names)
    return out


# Derived from the Graph class itself, so a member added to the model widens
# the probe with no edit here.  `dir()` misses the dataclass fields declared
# with a default_factory (`nodes`, `edges`), which are exactly the structural
# ones, so the field names are unioned in.
GRAPH_MEMBERS = (
    {name for name in dir(Graph) if not name.startswith("_")}
    | set(Graph.__dataclass_fields__)
)


def _members(root: Path, graph_only: bool) -> set[str]:
    found: set[str] = set()
    for path in sorted(root.rglob("*.py")):
        for qual, (_, names) in _recursive_defs(path.read_text(encoding="utf-8")).items():
            if graph_only and not (names & GRAPH_MEMBERS):
                continue
            found.add(f"{path.relative_to(REPO_ROOT).as_posix()} {qual}")
    return found


def recursive_functions_in_views() -> set[str]:
    """Every recursive function in mapper/views, by call cycle of any length.

    C-31: a hand-listed set omits the member that fails.  Increment 2 shipped
    this over `mapper/views/`; A-6 keeps it and adds the wider probe below.
    """
    return _members(VIEWS_DIR, graph_only=False)


def recursive_graph_traversals_in_mapper() -> set[str]:
    """A-6 — every recursive traversal of a Graph anywhere in `mapper/`.

    The root is the traversal SURFACE, not a directory someone chose.  A
    derived probe with a hand-picked root is not a derived probe: it reports an
    empty result with the same confidence either way.  Increment 2's root was
    `mapper/views/`, and `mapper/widgets/rail.py` was outside it.
    """
    return _members(MAPPER_DIR, graph_only=True)


# A-3 deferred `Graph.resolve_document` to increment 3, which opens `model.py`.
# Increment 3 CLOSED it, so the deferral list is gone rather than emptied: an
# empty exception set makes `deferred <= census` true for every census, and a
# guard that cannot fail is worse than no guard.  The assertion it carried — that
# no recursive Graph traversal hides behind a deferral — is now carried in
# stronger form by `test_tc_r29_...`, which subtracts nothing.


def test_tc_r10_the_ast_derivation_finds_the_functions_it_is_supposed_to_find():
    """The oracle's own guard: an empty result must mean "none", not "blind".

    Four shapes, because Increment 2's scanner saw only the first of them and
    measured `[]` on the second and third (finding F3).  The last two are the
    negative controls without which the probe could be reporting everything.
    """
    nl = chr(10)

    self_recursive = (
        f"def walk(g, nid, depth):{nl}"
        f"    for c in g.children_of(nid):{nl}"
        f"        walk(g, c, depth + 1){nl}"
    )
    assert set(_recursive_defs(self_recursive)) == {"walk"}

    nested = (
        f"def render(self):{nl}"
        f"    def tag(nid, grey):{nl}"
        f"        for c in self.graph.children_of(nid):{nl}"
        f"            tag(c, grey){nl}"
        f"    tag('a', 'x'){nl}"
    )
    assert set(_recursive_defs(nested)) == {"render.tag"}

    mutual = (
        f"def ping(g, nid):{nl}"
        f"    for c in g.children_of(nid):{nl}"
        f"        pong(g, c){nl}"
        f"{nl}"
        f"def pong(g, nid):{nl}"
        f"    ping(g, nid){nl}"
    )
    assert set(_recursive_defs(mutual)) == {"ping", "pong"}, (
        "a mutually recursive pair is recursion; increment 2's scanner reported []"
    )

    aliased = (
        f"def walk(g, nid):{nl}"
        f"    for c in g.children_of(nid):{nl}"
        f"        _alias(g, c){nl}"
        f"{nl}"
        f"_alias = walk{nl}"
    )
    assert set(_recursive_defs(aliased)) == {"walk"}, (
        "recursion through a module-level alias is recursion"
    )

    straight = (
        f"def rows(g):{nl}"
        f"    return [nid for nid in g.nodes]{nl}"
    )
    assert set(_recursive_defs(straight)) == set()

    chained = (
        f"class Thing(Base):{nl}"
        f"    def __init__(self, g):{nl}"
        f"        super().__init__(){nl}"
        f"        self.graph = g{nl}"
    )
    assert set(_recursive_defs(chained)) == set(), (
        "super().__init__() targets the base class; it is never a self-call"
    )


def test_tc_r10_the_graph_filter_keeps_the_probe_from_reporting_everything():
    """The filter's own control: recursive-and-graph-touching, both conjuncts.

    Without this, a filter that matched nothing would make the wide probe
    silently empty, and a filter that matched everything would make it useless.
    """
    nl = chr(10)
    walks_a_graph = (
        f"def walk(g, nid):{nl}"
        f"    for c in g.children_of(nid):{nl}"
        f"        walk(g, c){nl}"
    )
    walks_nothing = (
        f"def countdown(n):{nl}"
        f"    return 0 if n <= 0 else countdown(n - 1){nl}"
    )
    for source, touches in ((walks_a_graph, True), (walks_nothing, False)):
        found = _recursive_defs(source)
        assert set(found) == {"walk"} if touches else set(found) == {"countdown"}
        hit = bool(next(iter(found.values()))[1] & GRAPH_MEMBERS)
        assert hit is touches

    assert "children_of" in GRAPH_MEMBERS and "nodes" in GRAPH_MEMBERS


def test_tc_r11_no_graph_traversal_in_views_is_recursive():
    """LLR-R02.1 — every traversal in mapper/views is iterative.

    The five that shipped were radial._leaves, radial.place, radial.tag,
    layered._tree_layout.walk and outline.walk.  They are not named in the
    assertion on purpose: the set is derived, so adding a sixth reddens this.
    """
    assert recursive_functions_in_views() == set()


def test_tc_r29_no_recursive_graph_traversal_anywhere_in_mapper():
    """A-6 / A-3 — the widened derivation, rooted at the traversal surface.

    Increment 2's root was the `mapper/views/` directory and this probe was
    RED on the tree it handed over, with three members: `rail.py`'s
    `visible_rows.walk`, `factory.py`'s `_tree_lines.walk` and `model.py`'s
    `Graph.resolve_document`.  Increment 3 closed the last of them, so the
    assertion no longer subtracts a deferral list — nothing is named on either
    side, and a fourth member anywhere in `mapper/` reddens this.
    """
    assert recursive_graph_traversals_in_mapper() == set()


# --------------------------------------------------------------------------
# LLR-R02.2 — the memoised _leaves agrees with the recursive one


def _shipped_leaves(graph: Graph, nid: str) -> int:
    """The pre-repair implementation, verbatim, as the positive control.

    A rewrite is only correct if it agrees with the original everywhere the
    original terminated; a rewrite that merely stops crashing could be
    returning anything.
    """
    children = graph.children_of(nid)
    if not children:
        return 1
    return sum(_shipped_leaves(graph, c) for c in children)


def test_tc_r13_leaves_agrees_with_the_shipped_recursive_implementation(tmp_path):
    """LLR-R02.2 — positive control over several shapes, legacy.mmd included."""
    shapes = {
        "single node": _from_pairs("solo", []),
        "shallow chain": _chain(3),
        # Kept modest on purpose: the shipped implementation is quadratic and
        # calls Graph.children_of, which rescans every edge, so a long chain
        # costs minutes here.  Depth is AT-R04's subject; this is about values.
        "deep-but-survivable chain": _chain(150),
        "star": _from_pairs("r", [("r", f"c{i}") for i in range(12)]),
        "balanced tree": _balanced(300),
        "diamond": _from_pairs("a", [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]),
        "uneven": _from_pairs(
            "r", [("r", "a"), ("r", "b"), ("a", "a1"), ("a", "a2"), ("a1", "a1x")]
        ),
        "legacy.mmd": _legacy_graph(tmp_path),
    }
    # Every shape here is one the shipped implementation terminates on, which is
    # the scope LLR-R02.2 states.  Where it does not terminate there is nothing
    # to agree with, and that region is AT-R04's subject.
    compared = 0
    for label, graph in shapes.items():
        for nid in graph.nodes:
            compared += 1
            assert radial_mod._leaves(graph, nid) == _shipped_leaves(graph, nid), (
                f"{label}: memoised _leaves disagrees with the recursive original "
                f"at node {nid}"
            )
    # Guard against a vacuous pass on an empty or truncated shape set.
    assert compared == sum(len(g.nodes) for g in shapes.values()) >= 480, compared


# --------------------------------------------------------------------------
# AT-R04 — a deep acyclic map renders and never raises RecursionError


@pytest.mark.parametrize("name,renderer", RENDERERS)
def test_at_r04_a_deep_acyclic_chain_renders_through_the_shipped_surface(name, renderer):
    """AT-R04 — depth 5000, parsed by the shipped parser, drawn, no crash."""
    graph = parse(_deep_chain_source(DEEP))
    assert len(graph.nodes) == DEEP + 1

    started = time.perf_counter()
    text = renderer().render(graph, ViewState(selected_id="n0", w=80, h=24))
    elapsed = time.perf_counter() - started

    assert text.plain.strip(), f"{name} produced nothing"
    assert elapsed < RENDER_BOUND_SECONDS, f"{name} took {elapsed:.3f}s"


@pytest.mark.parametrize("name,renderer", RENDERERS)
def test_at_r04_depth_safety_does_not_depend_on_the_recursion_limit(name, renderer):
    """The declared plausible-weaker arm, neutralised by construction.

    `sys.setrecursionlimit(bigger)` is the tempting non-fix: it moves the crash
    instead of removing it.  This test *lowers* the limit around the render, so
    any surviving recursion deeper than the headroom dies — an implementation
    that "fixed" depth by raising the limit cannot pass a test that lowers it.
    """
    graph = _chain(DEEP)
    headroom = 120
    previous = sys.getrecursionlimit()
    sys.setrecursionlimit(_stack_depth() + headroom)
    try:
        text = renderer().render(graph, ViewState(selected_id="n0", w=80, h=24))
    finally:
        sys.setrecursionlimit(previous)
    assert text.plain.strip(), f"{name} produced nothing under a pinned limit"


# The traversals are flat loops, so the only Python nesting left in a render is
# the renderer's own call plus Rich's Text machinery.  Measured on the DEEP
# chain: radial 5, layered 5, outline 5.  The declared ceiling leaves room for
# ordinary refactoring and is still two orders of magnitude below DEEP.
MAX_CALL_DEPTH = 40


@pytest.mark.parametrize("name,renderer", RENDERERS)
def test_at_r04_a_render_never_nests_deeper_than_the_declared_call_depth(
    name, renderer
):
    """The arm-proof form of AT-R04's plausible-weaker counterfactual.

    `sys.setrecursionlimit(bigger)` moves the crash rather than removing it, and
    an implementation that raises the limit from inside `render` even survives a
    test that pins the limit from outside.  It cannot survive being counted: a
    traversal that recurses once per level reaches depth DEEP here, and DEEP is
    5000.
    """
    graph = _chain(DEEP)
    text, peak = _peak_call_depth(
        lambda: renderer().render(graph, ViewState(selected_id="n0", w=80, h=24))
    )
    assert text.plain.strip(), f"{name} produced nothing"
    assert peak <= MAX_CALL_DEPTH, f"{name} nested {peak} frames deep"


# --------------------------------------------------------------------------
# LLR-R02.1's other half — iterative is not enough; the traversal needs a bound


# Four shapes, not one.  Increment 2 drove only `entry_in_cycle`, which all
# three renderers catch in the same place, so the node could not tell a guard
# that handles one shape from a guard that handles cycles (increment 2 review,
# finding F2).  Each entry is (root, edges).
CYCLE_SHAPES = {
    "entry_in_cycle": ("a", [("a", "b"), ("b", "c"), ("c", "a")]),
    "self_loop_below": ("r", [("r", "a"), ("a", "a")]),
    "cycle_off_root": ("r", [("r", "a"), ("a", "b"), ("b", "c"), ("c", "a")]),
    "cycle_in_a_disconnected_component": ("r", [("r", "a"), ("p", "q"), ("q", "p")]),
}

REACHABLE_CYCLE_SHAPES = tuple(
    name for name in CYCLE_SHAPES if name != "cycle_in_a_disconnected_component"
)

# The disconnected component is the shape where the three renderers legitimately
# differ, so it is asserted by identity rather than absorbed.  Measured, on this
# tree and on `master` both:
#
#   radial   ValueError  — its node pass visits every node, not only the
#                          component the root reaches, so it meets the cycle
#   layered  KeyError    — PRE-EXISTING on `master`, verified by running the
#                          `master` sources: `_tree_layout` indexes a node it
#                          never placed.  Not a regression and not this
#                          increment's file; recorded so that `Exception` cannot
#                          absorb it and so a change here reddens
#   outline  rendered    — it walks from the root and never reaches p or q
DISCONNECTED_COMPONENT_OUTCOMES = {
    "radial": "ValueError",
    "layered": "KeyError",
    "outline": "rendered",
}


@pytest.mark.parametrize("shape", sorted(REACHABLE_CYCLE_SHAPES))
@pytest.mark.parametrize("name,renderer", RENDERERS)
def test_tc_r12_a_cyclic_graph_raises_the_guard_and_names_it(name, renderer, shape):
    """The guard's IDENTITY, not merely that something was raised.

    A cyclic graph cannot reach a renderer through the store — HLR-R01 refuses
    it at load — but `_ImportPreviewScreen` builds one from a CSV without going
    near the parser, and that sink caught the RecursionError the recursion used
    to raise.  Turning the traversal into a plain loop turned that bounded crash
    into an unbounded hang, which is strictly worse.

    Increment 2's oracle was `pytest.raises(Exception)`, which an unrelated
    KeyError satisfies — and one measurably does, on the fourth shape below.
    So this asserts the exception type, the guard's own words, and that the
    node it names is really on the cycle.
    """
    root, pairs = CYCLE_SHAPES[shape]
    graph = _from_pairs(root, pairs)
    in_a_cycle = {parent for parent, _ in pairs} & {child for _, child in pairs}

    started = time.perf_counter()
    with pytest.raises(ValueError) as excinfo:
        renderer().render(graph, ViewState(selected_id=root, w=80, h=24))
    elapsed = time.perf_counter() - started

    assert not isinstance(excinfo.value, RecursionError)
    assert GUARD_MESSAGE in str(excinfo.value), str(excinfo.value)
    named = str(excinfo.value).split()[2].rstrip(":")
    assert named in in_a_cycle, f"{name} named {named}, which is not on the cycle"
    assert elapsed < RENDER_BOUND_SECONDS, f"{name} took {elapsed:.3f}s to give up"


@pytest.mark.parametrize("name,renderer", RENDERERS)
def test_tc_r12_a_cycle_the_renderer_never_visits_is_asserted_not_absorbed(
    name, renderer
):
    """Where a renderer legitimately never reaches the component, say so.

    Letting `pytest.raises(Exception)` stand in for this is what made increment
    2's node vacuous for `layered`, whose KeyError here has nothing to do with
    the cycle guard.
    """
    root, pairs = CYCLE_SHAPES["cycle_in_a_disconnected_component"]
    graph = _from_pairs(root, pairs)

    started = time.perf_counter()
    try:
        text = renderer().render(graph, ViewState(selected_id=root, w=80, h=24))
        outcome = "rendered"
    except Exception as exc:  # noqa: BLE001 - the identity is the assertion
        assert not isinstance(exc, RecursionError), f"{name} recursed on a cycle"
        outcome = type(exc).__name__
        text = None
    elapsed = time.perf_counter() - started

    assert outcome == DISCONNECTED_COMPONENT_OUTCOMES[name], (
        f"{name} answered {outcome}; the recorded outcome is "
        f"{DISCONNECTED_COMPONENT_OUTCOMES[name]}"
    )
    if outcome == "rendered":
        assert text.plain.strip()
    assert elapsed < RENDER_BOUND_SECONDS, f"{name} took {elapsed:.3f}s"


# --------------------------------------------------------------------------
# AT-R05 — a 3000-node tree renders inside the declared bound


@pytest.mark.parametrize("name,renderer", RENDERERS)
def test_at_r05_a_3000_node_tree_renders_within_the_declared_bound(name, renderer):
    graph = _balanced(3000)
    assert len(graph.nodes) == 3000

    started = time.perf_counter()
    text = renderer().render(graph, ViewState(selected_id="n0", w=140, h=45))
    elapsed = time.perf_counter() - started

    assert text.plain.strip(), f"{name} produced nothing"
    assert elapsed < RENDER_BOUND_SECONDS, (
        f"{name} took {elapsed:.3f}s, over the declared {RENDER_BOUND_SECONDS}s"
    )


# --------------------------------------------------------------------------
# LLR-R02.3 — past the declared bound, a declared degradation


def test_tc_r14_the_renderers_declare_one_shared_bound():
    """The three bounds are separate constants; drift between them reddens here."""
    bounds = {
        module.__name__: module.MAX_RENDER_NODES
        for module in (radial_mod, layered_mod, outline_mod)
    }
    assert len(set(bounds.values())) == 1, bounds


@pytest.mark.parametrize("name,renderer", RENDERERS)
def test_tc_r14_a_map_past_the_bound_degrades_in_spanish_and_does_not_raise(
    name, renderer
):
    """LLR-R02.3 — the notice names the size, the bound, and what was dropped."""
    bound = radial_mod.MAX_RENDER_NODES
    graph = _balanced(bound + 1)

    text = renderer().render(graph, ViewState(selected_id="n0", w=140, h=45))

    assert str(bound + 1) in text.plain
    assert str(bound) in text.plain
    assert OVER_BOUND in text.plain
    assert OMITTED in text.plain


@pytest.mark.parametrize("name,renderer", RENDERERS)
def test_tc_r14_a_map_at_the_bound_still_draws(name, renderer):
    """The discriminating negative: a bound that degrades everything is not a fix."""
    graph = _balanced(radial_mod.MAX_RENDER_NODES)

    text = renderer().render(graph, ViewState(selected_id="n0", w=140, h=45))

    assert OMITTED not in text.plain
    assert text.plain.strip()


# --------------------------------------------------------------------------
# C-53 — the false-failure arm: ordinary maps are untouched


@pytest.mark.parametrize("w,h", GOLDEN_SIZES)
@pytest.mark.parametrize("name,renderer", RENDERERS)
def test_c53_legacy_fixture_renders_identically_to_master(name, renderer, w, h, tmp_path):
    """A depth fix that changes normal output is a regression.

    Rule 12 of the batch's own pricing: a gate that false-fails correct work
    costs as much as one that passes wrong work, so the ordinary map is pinned
    against the bytes `master` produced — at four sizes, because the riskiest
    change of increment 2 is `layered.py`'s body height cap and that cap is a
    function of `h`.  One pinned size cannot see it move.
    """
    graph = _legacy_graph(tmp_path)
    text = renderer().render(graph, ViewState(selected_id="fin", w=w, h=h))
    assert _fingerprint(text) == MASTER_LEGACY_DIGESTS[(renderer.__name__, w, h)]


# ==========================================================================
# A-6 / increment 2b — the rail and the factory tree
#
# `OutlineRail.visible_rows`'s inner walk and `FactoryScreen._tree_lines`'s
# inner walk are recursive traversals of the same Graph, one frame per level,
# and both run where nothing catches them: the rail from Textual's compositor,
# the factory tree from `on_mount`.  Reproduced at depth 5000 with a positive
# control at depth 3, before anything below was written.


def _shipped_visible_rows(rail: OutlineRail) -> list[tuple[str, int]]:
    """`OutlineRail.visible_rows` as it shipped, verbatim, as the control.

    A rewrite is only correct if it agrees with the original everywhere the
    original terminated; a rewrite that merely stops crashing could be
    returning anything.
    """
    rows: list[tuple[str, int]] = []
    if rail.graph.root_id is None:
        return rows

    def walk(nid: str, depth: int) -> None:
        rows.append((nid, depth))
        if nid in rail.collapsed:
            return
        for child in rail.graph.children_of(nid):
            walk(child, depth + 1)

    walk(rail.graph.root_id, 0)
    return rows


def _shipped_subtree_missing(rail: OutlineRail, node_id: str) -> int:
    """`OutlineRail.subtree_missing` as it shipped, verbatim."""
    total = 0
    stack = [node_id]
    seen: set[str] = set()
    while stack:
        nid = stack.pop()
        if nid in seen or nid not in rail.graph.nodes:
            continue
        seen.add(nid)
        total += len(rail.graph.nodes[nid].ficha.missing_required(rail.graph.schema))
        stack.extend(rail.graph.children_of(nid))
    return total


def _shipped_tree_lines(screen: FactoryScreen) -> Text:
    """`FactoryScreen._tree_lines` as it shipped, verbatim."""
    lines: list[tuple[str, str]] = []
    block = f"bold {darkside.GROUND} on {darkside.ACCENT}"

    def walk(nid: str, depth: int) -> None:
        node = screen.graph.nodes[nid]
        prefix = "  " * depth + chr(0x25B8) + " "
        selected = nid == screen.nav.cursor
        title = escape(node.ficha.title or nid)
        lines.append(
            (f"{prefix}{title}" + chr(10), block if selected else darkside.INK)
        )
        for cid in screen.graph.children_of(nid):
            walk(cid, depth + 1)

    if screen.graph.root_id is not None:
        walk(screen.graph.root_id, 0)
    return Text.assemble(*lines)


def _shipped_max_depth(screen: FactoryScreen) -> int:
    """`FactoryScreen._depth` and `_max_depth` as they shipped, verbatim."""

    def depth_of(nid: str) -> int:
        depth = 0
        current = nid
        while True:
            parent = screen.graph.parent_of(current)
            if parent is None:
                return depth
            depth += 1
            current = parent

    return max((depth_of(nid) for nid in screen.graph.nodes), default=0)


def _equivalence_shapes(tmp_path) -> dict[str, Graph]:
    """Shapes the shipped implementations all terminate on.

    The diamond earns its place twice: it is the one shape where the memoised
    post-order sum could have changed an answer, and it is the shape that makes
    `_missing_map` decline and hand back to the exact walk.
    """
    return {
        "single node": _from_pairs("solo", []),
        "shallow chain": _chain(3),
        "deep-but-survivable chain": _chain(150),
        "star": _from_pairs("r", [("r", f"c{i}") for i in range(12)]),
        "balanced tree": _balanced(300),
        "diamond": _from_pairs("a", [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]),
        "uneven": _from_pairs(
            "r", [("r", "a"), ("r", "b"), ("a", "a1"), ("a", "a2"), ("a1", "a1x")]
        ),
        "legacy.mmd": _legacy_graph(tmp_path),
    }


def _collapsed_configurations(graph: Graph) -> list[set[str]]:
    """Collapse sets derived from the shape, never hand-listed per shape.

    `collapsed` is the input a wrongly keyed memo would expose, so the
    equivalence proof is taken over several of them rather than over the
    expanded tree alone.
    """
    internal = sorted({edge.parent_id for edge in graph.edges})
    configurations: list[set[str]] = [set(), set(internal)]
    if graph.root_id is not None:
        configurations.append({graph.root_id})
    for nid in internal[:4]:
        configurations.append({nid})
    if len(internal) >= 2:
        configurations.append(set(internal[:2]))
        configurations.append(set(internal[::2]))
    return configurations


def test_tc_r30_visible_rows_agrees_with_the_shipped_recursive_implementation(tmp_path):
    """LLR-R02.2's shape for the rail — a positive control over collapse sets."""
    compared = 0
    for label, graph in _equivalence_shapes(tmp_path).items():
        rail = OutlineRail()
        rail.graph = graph
        for collapsed in _collapsed_configurations(graph):
            rail.collapsed = set(collapsed)
            compared += 1
            assert rail.visible_rows() == _shipped_visible_rows(rail), (
                f"{label}: the iterative visible_rows disagrees with the "
                f"recursive original with {sorted(collapsed)} collapsed"
            )
    # Guard against a vacuous pass on an empty or truncated configuration set.
    assert compared >= 40, compared


def test_tc_r30_subtree_missing_agrees_with_the_shipped_implementation(tmp_path):
    """The memoised pass must answer what the deduplicated walk answered.

    The diamond is the discriminating case: a post-order sum counts the shared
    node twice, so a rewrite that always summed would redden here.
    """
    compared = 0
    shapes = _equivalence_shapes(tmp_path)
    for label, graph in shapes.items():
        rail = OutlineRail()
        rail.graph = graph
        for nid in graph.nodes:
            compared += 1
            assert rail.subtree_missing(nid) == _shipped_subtree_missing(rail, nid), (
                f"{label}: subtree_missing disagrees with the shipped walk at {nid}"
            )
    assert compared == sum(len(g.nodes) for g in shapes.values()) >= 480, compared


def test_tc_r30_the_memoised_pass_declines_a_shape_it_cannot_answer(tmp_path):
    """The fallback is load-bearing, so it is asserted rather than assumed.

    `_missing_map` returns None where a node has two parents, because there a
    post-order sum and the deduplicated walk genuinely differ.  Without this
    node, a later change that dropped the check would be invisible: every other
    shape in the suite is a forest.
    """
    rail = OutlineRail()
    rail.graph = _from_pairs("a", [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")])
    assert rail._missing_map(rail._child_index()) is None

    rail.graph = _from_pairs("a", [("a", "b"), ("a", "c")])
    assert rail._missing_map(rail._child_index()) is not None


def test_tc_r31_tree_lines_agrees_with_the_shipped_recursive_implementation(tmp_path):
    """The factory tree, byte for byte against its recursive original."""
    compared = 0
    for label, graph in _equivalence_shapes(tmp_path).items():
        screen = FactoryScreen(graph)
        for cursor in [None, graph.root_id, *sorted(graph.nodes)[:3]]:
            screen.nav.cursor = cursor
            compared += 1
            assert _fingerprint(screen._tree_lines()) == _fingerprint(
                _shipped_tree_lines(screen)
            ), f"{label}: the iterative tree disagrees with cursor {cursor}"
    assert compared >= 30, compared


def _shipped_depth(screen: FactoryScreen, nid: str) -> int:
    """`FactoryScreen._depth` as it shipped, verbatim."""
    depth = 0
    current = nid
    while True:
        parent = screen.graph.parent_of(current)
        if parent is None:
            return depth
        depth += 1
        current = parent


def test_tc_r31_max_depth_agrees_with_the_shipped_implementation(tmp_path):
    """The one-pass depth map must answer what the per-node chain walk answered.

    Both halves: `_depth` node by node, and the `_max_depth` that memoises it.
    A memo shared across chains is the thing most likely to be off by one, so
    every node is compared rather than only the maximum.
    """
    compared = 0
    shapes = _equivalence_shapes(tmp_path)
    for label, graph in shapes.items():
        screen = FactoryScreen(graph)
        assert screen._max_depth() == _shipped_max_depth(screen), label
        for nid in graph.nodes:
            compared += 1
            assert screen._depth(nid) == _shipped_depth(screen, nid), (
                f"{label}: _depth disagrees with the shipped chain walk at {nid}"
            )
    assert compared == sum(len(g.nodes) for g in shapes.values()) >= 480, compared


# --------------------------------------------------------------------------
# C-53 for this increment's own two files


@pytest.mark.parametrize("collapsed", sorted(MASTER_RAIL_DIGESTS))
def test_c53_the_rail_renders_legacy_identically_to_master(collapsed, tmp_path):
    """A depth fix that changes the ordinary rail is a regression.

    Varied over collapse sets rather than over terminal sizes: the rail renders
    at RAIL_WIDTH whatever the terminal is, and `collapsed` is the input a memo
    keyed on the wrong thing would corrupt.
    """
    rail = OutlineRail()
    rail.graph = _legacy_graph(tmp_path)
    rail.cursor = "fin"
    rail.collapsed = set(collapsed)
    assert _fingerprint(rail.render()) == MASTER_RAIL_DIGESTS[collapsed]


@pytest.mark.parametrize("size", ((140, 45), (80, 24), (300, 120)))
async def test_c53_the_rail_is_byte_identical_at_every_terminal_size(size, tmp_path):
    """Through the composed screen, so the compositor's own call is the one read."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        app.store.save("legacy2", _legacy_graph(tmp_path))
        app.push_screen(MapScreen("legacy2"))
        await pilot.pause()
        await pilot.pause()
        rail = app.screen.query_one("#map-rail", OutlineRail)
        rail.cursor = "fin"
        assert _fingerprint(rail.render()) == MASTER_RAIL_DIGESTS[()]


def test_c53_the_factory_tree_renders_legacy_identically_to_master(tmp_path):
    screen = FactoryScreen(_legacy_graph(tmp_path))
    screen.nav.cursor = "fin"
    assert _fingerprint(screen._tree_lines()) == MASTER_FACTORY_TREE_DIGEST


# --------------------------------------------------------------------------
# AT-R16 — depth 5000 through the composed surface, not through a direct call


def _count_graph_scans(monkeypatch, name: str) -> dict[str, int]:
    """Count calls to a `Graph` accessor that rescans the whole edge list."""
    calls = {"n": 0}
    original = getattr(Graph, name)

    def counting(self, node_id):
        calls["n"] += 1
        return original(self, node_id)

    monkeypatch.setattr(Graph, name, counting)
    return calls


# One full edge-list scan per render is acceptable; one per row is the defect.
# The rewritten code indexes adjacency once and calls neither accessor, so the
# measured count is 0.  The ceiling leaves room for an incidental call without
# leaving room for a per-row rescan.
MAX_EDGE_LIST_SCANS = 4


def test_at_r16_the_rail_render_scans_the_edge_list_a_bounded_number_of_times(
    monkeypatch,
):
    """The memo is pinned by a COUNT, not by a clock.

    `subtree_missing` used to be called once per visible row, and each call
    re-walked the branch through `Graph.children_of`, which rescans every edge:
    0.016 s at depth 100, 5.616 s at depth 800, ~8x per doubling — cubic.  De-
    recursing `visible_rows` alone would have turned a bounded RecursionError
    into a ~23-minute hang, which is increment 2's 23.7 GB lesson in a third
    shape.  A wall clock catches that on this machine and misses it on a faster
    one; the number of full edge-list scans is the same on every machine.
    """
    rail = _rail_for(_chain(400))
    calls = _count_graph_scans(monkeypatch, "children_of")
    rail.render()
    assert calls["n"] <= MAX_EDGE_LIST_SCANS, (
        f"the rail rescanned the edge list {calls['n']} times for 401 rows"
    )


def test_at_r16_max_depth_scans_the_edge_list_a_bounded_number_of_times(monkeypatch):
    """The same pin for the factory: `_depth` per node, `parent_of` per step.

    Measured before the change: 0.004 s at depth 100, 1.717 s at depth 800.
    """
    screen = FactoryScreen(_chain(400))
    calls = _count_graph_scans(monkeypatch, "parent_of")
    screen._max_depth()
    assert calls["n"] <= MAX_EDGE_LIST_SCANS, (
        f"_max_depth rescanned the edge list {calls['n']} times for 401 nodes"
    )


def test_tc_r30_the_indent_cap_cannot_change_a_rendered_row(tmp_path):
    """The cap is safe only because `fit` truncates — assert that against `_body`.

    `_body` builds `"  " * min(depth, RAIL_WIDTH)` rather than the true indent,
    because a deep chain is otherwise quadratic in characters: 3.257 s at depth
    5000 against 0.091 s capped.  That is sound only while the capped indent and
    the TRUE indent produce the same row after `darkside.fit`.

    **This node drives the real `_body` and compares its rows against rows built
    from the UNCAPPED indent.**  The previous version recomputed
    `min(depth, RAIL_WIDTH)` in its own body and compared two expressions it had
    written itself, so `rail.py`'s cap never appeared in the predicate at all: the
    increment 2b review mutated the cap from `RAIL_WIDTH` to `6` in a clone of the
    tree and the whole 356-node suite stayed GREEN, while 33 depths rendered
    wrong.  A predicate invariant under the change it gates cannot gate it
    (C-40 limb 1).  The oracle below is independent of the cap's value, so any cap
    too small to reach the truncation point reddens this node.
    """
    graph = _chain(40)
    rail = OutlineRail()
    rail.show(graph, graph.root_id)
    rendered = rail.render().plain.split("\n")

    rows = rail.visible_rows()
    assert len(rows) == 41, f"expected a 41-row chain, got {len(rows)}"

    width = RAIL_WIDTH - 4
    # The header is two lines ("mapa · Nn · M faltan" plus a blank), so the first
    # node row starts at index 2.  Asserted rather than assumed.
    assert rendered[0].startswith("mapa"), rendered[0]
    offset = 2

    checked = 0
    for position, (nid, depth) in enumerate(rows):
        node = graph.nodes[nid]
        marker = "  " if not graph.children_of(nid) else "▾ "
        label = darkside.plain(node.ficha.title or nid)
        # The oracle uses the TRUE indent — the thing the cap replaces.
        expected = darkside.fit("  " * depth + marker + label, width)
        actual = rendered[offset + position][:len(expected)]
        assert actual == expected, (
            f"depth {depth}: rendered row {actual!r} does not match the row the "
            f"uncapped indent would produce, {expected!r} — the cap in "
            f"`_body` is too small to be invisible"
        )
        checked += 1
    assert checked == 41, f"the oracle checked {checked} rows, expected 41"


@pytest.mark.slow
async def test_at_r16_the_rail_survives_a_depth_5000_map_through_the_composed_screen(
    tmp_path,
):
    """A-6's acceptance: the rail is composed on every map, outside every guard.

    The oracle is that the application is still running afterwards.  A
    RecursionError raised inside `OutlineRail.render` escapes the Textual
    message pump exactly as S-01a did, which is what "it kills the app" means.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 45)) as pilot:
        await pilot.pause()
        app.store.save("deep", _chain(DEEP))
        app.push_screen(MapScreen("deep"))
        await pilot.pause()
        await pilot.pause()

        rail = app.screen.query_one("#map-rail", OutlineRail)
        started = time.perf_counter()
        text = rail.render()
        elapsed = time.perf_counter() - started

        assert app.is_running, "the message pump died on a deep map"
        assert len(rail.visible_rows()) == DEEP + 1
        assert text.plain.strip()
        assert elapsed < RENDER_BOUND_SECONDS, f"the rail took {elapsed:.3f}s"


@pytest.mark.slow
def test_at_r16_the_factory_tree_survives_a_depth_5000_map():
    """The tree PANE, not the composed screen — and the difference is the point.

    Increment 2b's review (F3) found this node asserting strictly less than its
    rail sibling above, which drives `app.run_test`.  At that time the composed
    factory screen still died at depth in `_refresh` → `_preview` →
    `Graph.resolve_document`, deferred to increment 3 by amendment A-3.
    Increment 3 closed it, and the composed-screen node below is what says so;
    this one stays as the pane-level measurement it always was.
    """
    graph = _chain(DEEP)
    screen = FactoryScreen(graph)

    started = time.perf_counter()
    text = screen._tree_lines()
    elapsed = time.perf_counter() - started

    assert len(text.plain.splitlines()) == DEEP + 1
    assert screen._max_depth() == DEEP
    assert elapsed < FACTORY_TREE_BOUND_SECONDS, f"the factory tree took {elapsed:.3f}s"


@pytest.mark.slow
async def test_at_r16b_the_factory_screen_survives_a_depth_5000_map_composed(tmp_path):
    """A-3's acceptance through the COMPOSED screen (increment 2b, finding F3).

    The pane-level node above calls `_tree_lines()` directly.  `_refresh` calls
    `_preview()` as well, and `_preview` goes through `Graph.resolve_document`,
    which was recursive until increment 3 — so the composed screen died at depth
    while the pane-level node stayed green, and nothing said the two differed.

    The oracle is that the message pump is still running after the screen has
    actually mounted and refreshed, which is what "it kills the screen" means.
    """
    graph = _chain(DEEP)
    graph.documents = {"doc": Document(name="doc", source="{{k}}", tags={"k": "v"})}

    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 45)) as pilot:
        await pilot.pause()
        screen = FactoryScreen(graph)
        app.push_screen(screen)
        await pilot.pause()
        await pilot.pause()

        # Drive the cursor deep — the shallow default would not reach the chain.
        screen.nav.cursor = f"n{DEEP - 1}"
        started = time.perf_counter()
        screen._refresh()
        elapsed = time.perf_counter() - started

        assert app.is_running, "the message pump died on a deep map"
        assert screen._preview().plain.strip()
        assert elapsed < FACTORY_TREE_BOUND_SECONDS, f"the refresh took {elapsed:.3f}s"


DEEP_TARGETS = (
    ("rail.render", lambda graph: _rail_for(graph).render()),
    ("rail.visible_rows", lambda graph: _rail_for(graph).visible_rows()),
    ("rail.subtree_missing", lambda graph: _rail_for(graph).subtree_missing("n0")),
    ("factory._tree_lines", lambda graph: FactoryScreen(graph)._tree_lines()),
    ("factory._max_depth", lambda graph: FactoryScreen(graph)._max_depth()),
    ("factory._depth", lambda graph: FactoryScreen(graph)._depth(f"n{DEEP}")),
)


def _rail_for(graph: Graph) -> OutlineRail:
    rail = OutlineRail()
    rail.graph = graph
    rail.cursor = graph.root_id
    return rail


@pytest.mark.slow
@pytest.mark.parametrize("name,call", DEEP_TARGETS, ids=[n for n, _ in DEEP_TARGETS])
def test_at_r16_depth_safety_does_not_depend_on_the_recursion_limit(name, call):
    """The declared plausible-weaker arm, neutralised by construction.

    `sys.setrecursionlimit(bigger)` moves the crash instead of removing it.
    This *lowers* the limit around the call, so any surviving recursion deeper
    than the headroom dies.
    """
    graph = _chain(DEEP)
    previous = sys.getrecursionlimit()
    sys.setrecursionlimit(_stack_depth() + 120)
    try:
        call(graph)
    finally:
        sys.setrecursionlimit(previous)


@pytest.mark.slow
@pytest.mark.parametrize("name,call", DEEP_TARGETS, ids=[n for n, _ in DEEP_TARGETS])
def test_at_r16_a_traversal_never_nests_deeper_than_the_declared_call_depth(name, call):
    """The arm-proof form: counting frames, which no limit trick can dodge.

    Increment 2 measured that recursion plus `sys.setrecursionlimit` raised
    from INSIDE the call stays green against a deep-chain test and against a
    test that pins the limit from outside.  It cannot survive being counted.
    """
    graph = _chain(DEEP)
    _, peak = _peak_call_depth(lambda: call(graph))
    assert peak <= MAX_CALL_DEPTH, f"{name} nested {peak} frames deep"


# --------------------------------------------------------------------------
# TC-R32 — a cyclic graph terminates, in its own process, under two ceilings
#
# Increment 2's lesson, third instance: converting recursion to iteration turns
# a bounded crash into an unbounded hang.  A hang is not a test failure, it is a
# test that never reports, so termination is asserted from OUTSIDE the process
# under a wall clock, and the allocation that a hang drags with it — increment 2
# reached 23.7 GB resident — is bounded from inside by a watchdog.

CYCLE_WALL_CLOCK_SECONDS = 90.0
CYCLE_RSS_CEILING_BYTES = 800 * 1024 * 1024
"""Measured: the child reports 52.1 MB resident after importing Textual and Rich.

The ceiling is ~15x that, and ~30x below the 23.7 GB increment 2 measured when
an unbounded loop met a cyclic graph, so it separates "works" from "ran away"
without tracking ordinary interpreter growth.
"""


def _rss_bytes() -> int:
    """Resident set size of THIS process. Stdlib only — psutil is not a dep.

    It RAISES rather than returning 0 when the platform call fails.  The first
    version of this returned 0 on every call, because `GetCurrentProcess`
    defaults to a C `int` restype and its pseudo-handle was truncated on 64-bit
    — so the watchdog below could never fire and the ceiling was decoration.
    A memory oracle that silently reads zero is worse than none.
    """
    if sys.platform == "win32":
        import ctypes
        import ctypes.wintypes

        class _Counters(ctypes.Structure):
            _fields_ = [
                ("cb", ctypes.wintypes.DWORD),
                ("PageFaultCount", ctypes.wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        kernel32 = ctypes.windll.kernel32
        kernel32.GetCurrentProcess.restype = ctypes.c_void_p
        read = ctypes.windll.psapi.GetProcessMemoryInfo
        read.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_Counters),
            ctypes.wintypes.DWORD,
        ]
        read.restype = ctypes.wintypes.BOOL

        counters = _Counters()
        counters.cb = ctypes.sizeof(_Counters)
        if not read(kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
            raise OSError("GetProcessMemoryInfo failed; the RSS ceiling is blind")
        return int(counters.WorkingSetSize)

    import resource

    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(peak if sys.platform == "darwin" else peak * 1024)


def test_tc_r32_the_rss_ceiling_can_actually_fire():
    """The watchdog's own positive control — C-55, applied to a ceiling.

    A ceiling that never fires and a graph that never runs away produce the same
    green.  This drives the same `_cycle_child` with the ceiling set below the
    interpreter's own footprint, so the watchdog must trip; and it reads a
    plausible RSS in this process, so the reading itself is not a constant.
    """
    resident = _rss_bytes()
    assert 8 * 1024 * 1024 < resident < CYCLE_RSS_CEILING_BYTES, resident

    command = [
        sys.executable,
        "-c",
        "from tests.test_repair_depth import _cycle_child; "
        "_cycle_child('entry_in_cycle')",
    ]
    done = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env={
            **os.environ,
            "PYTHONUTF8": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "CYCLE_RSS_CEILING_BYTES": str(4 * 1024 * 1024),
        },
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=CYCLE_WALL_CLOCK_SECONDS,
    )
    assert "RSS-EXCEEDED" in done.stdout, done.stdout[-2000:]
    assert "_done" not in done.stdout, "the watchdog fired but did not stop the child"


def _structural_graph_members() -> set[str]:
    """Graph's structure surface, derived from Graph's own source.

    Its data fields, plus every Graph method that LOOPS over one of them.  The
    loop is the point: `resolve_document` reads `parent_of` but does not iterate
    the structure, and `_preview` reads `nodes` with a dict lookup — neither is
    a traversal, and neither is dragged in.
    """
    fields = set(Graph.__dataclass_fields__)
    members = set(fields)
    source = Path(inspect.getsourcefile(Graph)).read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(source)):
        if not (isinstance(node, ast.ClassDef) and node.name == Graph.__name__):
            continue
        for method in node.body:
            if not isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for inner in ast.walk(method):
                if isinstance(inner, (ast.For, ast.AsyncFor)):
                    iterables = [inner.iter]
                elif isinstance(
                    inner,
                    (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp),
                ):
                    iterables = [gen.iter for gen in inner.generators]
                else:
                    continue
                if any(_referenced_names(it) & fields for it in iterables):
                    members.add(method.name)
    return members


TRAVERSAL_FILES = (
    MAPPER_DIR / "widgets" / "rail.py",
    MAPPER_DIR / "screens" / "factory.py",
)


def graph_touching_methods() -> set[tuple[str, str]]:
    """Every method of this increment's two files that reaches Graph structure.

    Derived, and closed over calls inside the same class: a method that only
    delegates still runs the traversal, so `OutlineRail.render` is in the set
    because `_body` is, and `FactoryScreen._tree_lines` because `_tree_text` is.
    An owner of `""` means a module-level function, which the harness cannot
    instantiate and therefore reports rather than skips.
    """
    structural = _structural_graph_members()
    found: set[tuple[str, str]] = set()
    for path in TRAVERSAL_FILES:
        defs: dict[str, tuple] = {}
        aliases: dict[str, set[str]] = {}
        _collect(ast.parse(path.read_text(encoding="utf-8")), [], defs, aliases)
        owned = {
            qual: (dscope[0] if dscope else "", dname, calls, referenced)
            for qual, (dscope, dname, calls, referenced, _) in defs.items()
            if len(dscope) <= 1
        }
        here = {
            (owner, dname)
            for owner, dname, _, referenced in owned.values()
            if referenced & structural
        }
        widening = True
        while widening:
            widening = False
            for owner, dname, calls, _ in owned.values():
                if (owner, dname) in here:
                    continue
                if calls & {name for other, name in here if other == owner}:
                    here.add((owner, dname))
                    widening = True
        found |= here
    return found


def _cycle_child(shape: str) -> None:
    """Drive every derived Graph-touching method on one cyclic graph.

    Runs as its own process: a hang is bounded by the parent's wall clock, and
    a runaway allocation by this watchdog.  Nothing here asserts — the parent
    reads a verdict per method from stdout, so no verdict is the process exit
    code.
    """
    import threading

    ceiling = int(os.environ["CYCLE_RSS_CEILING_BYTES"])

    def watch() -> None:
        while True:
            resident = _rss_bytes()
            if resident > ceiling:
                print(f"VERDICT _watchdog RSS-EXCEEDED {resident}", flush=True)
                os._exit(9)
            time.sleep(0.05)

    threading.Thread(target=watch, daemon=True).start()

    root, pairs = CYCLE_SHAPES[shape]
    graph = _from_pairs(root, pairs)
    rail = _rail_for(graph)
    screen = FactoryScreen(graph)
    instances = {"OutlineRail": rail, "FactoryScreen": screen, "_Nav": screen.nav}
    arguments = {
        "node_id": root,
        "nid": root,
        "graph": graph,
        "index": rail._child_index(),
        "cursor": root,
    }

    for owner, method in sorted(graph_touching_methods()):
        instance = instances.get(owner)
        if instance is None:
            print(f"VERDICT {owner}.{method} NO-INSTANCE", flush=True)
            continue
        bound = getattr(instance, method)
        required = [
            name
            for name, spec in inspect.signature(bound).parameters.items()
            if spec.default is inspect.Parameter.empty
            and spec.kind
            in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ]
        unknown = [name for name in required if name not in arguments]
        if unknown:
            print(f"VERDICT {owner}.{method} NO-ARGUMENT {unknown}", flush=True)
            continue
        started = time.perf_counter()
        try:
            bound(*(arguments[name] for name in required))
            verdict = "RETURNED"
        except BaseException as exc:  # noqa: BLE001 - the identity is the report
            verdict = type(exc).__name__
        print(
            f"VERDICT {owner}.{method} {verdict} "
            f"{time.perf_counter() - started:.4f}",
            flush=True,
        )
    print(f"VERDICT _done OK {_rss_bytes()}", flush=True)


def _run_cycle_child(shape: str) -> dict[str, str]:
    command = [
        sys.executable,
        "-c",
        "from tests.test_repair_depth import _cycle_child; "
        f"_cycle_child({shape!r})",
    ]
    environment = {
        **os.environ,
        "PYTHONUTF8": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "CYCLE_RSS_CEILING_BYTES": str(CYCLE_RSS_CEILING_BYTES),
    }
    try:
        done = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=CYCLE_WALL_CLOCK_SECONDS,
        )
    except subprocess.TimeoutExpired:
        pytest.fail(
            f"{shape}: still running after {CYCLE_WALL_CLOCK_SECONDS}s. That is a "
            "hang, which is what an iterative traversal without a bound does to "
            "a cyclic graph"
        )
    verdicts = {}
    for line in done.stdout.splitlines():
        if line.startswith("VERDICT "):
            _, target, verdict = line.split(maxsplit=2)
            verdicts[target] = verdict.split()[0]
    assert "_done" in verdicts, (
        f"{shape}: the child never finished.{chr(10)}"
        f"stdout:{chr(10)}{done.stdout}{chr(10)}stderr:{chr(10)}{done.stderr}"
    )
    return verdicts


@pytest.mark.parametrize("shape", sorted(CYCLE_SHAPES))
def test_tc_r32_every_graph_touching_method_terminates_on_a_cyclic_graph(shape):
    """Four cycle shapes, every derived method, one process each.

    The set of methods is derived, so this is also the census that answers "did
    you check every traversal in the file, or only the one that was named".
    """
    verdicts = _run_cycle_child(shape)
    covered = {
        f"{owner}.{method}" for owner, method in graph_touching_methods()
    }
    assert covered <= set(verdicts), sorted(covered - set(verdicts))
    for target in sorted(covered):
        verdict = verdicts[target]
        assert verdict not in ("NO-INSTANCE", "NO-ARGUMENT"), (
            f"{target}: the harness could not drive it, so its termination on a "
            f"cyclic graph is unmeasured ({verdict})"
        )
        assert verdict != "RecursionError", f"{target} recursed on {shape}"
    assert "RSS-EXCEEDED" not in verdicts.values()


@pytest.mark.parametrize("shape", sorted(REACHABLE_CYCLE_SHAPES))
def test_tc_r32_the_rail_paints_a_spanish_notice_instead_of_propagating(shape):
    """A-6's actual defect: the compositor calls `render`, and nothing catches it.

    The traversals raise, which is what increment 2's renderers do and what
    makes the guard's identity assertable.  `render` is the surface Textual
    calls, so it is the one that must never propagate.
    """
    root, pairs = CYCLE_SHAPES[shape]
    rail = _rail_for(_from_pairs(root, pairs))

    with pytest.raises(ValueError) as excinfo:
        rail.visible_rows()
    assert GUARD_MESSAGE in str(excinfo.value)

    text = rail.render()
    assert CYCLE_NOTICE in text.plain, text.plain
    assert chr(0xF3) not in CYCLE_NOTICE  # the notice needs no accent to survive


@pytest.mark.parametrize("shape", sorted(REACHABLE_CYCLE_SHAPES))
def test_tc_r32_the_factory_tree_paints_a_spanish_notice_instead_of_propagating(shape):
    root, pairs = CYCLE_SHAPES[shape]
    screen = FactoryScreen(_from_pairs(root, pairs))

    with pytest.raises(ValueError) as excinfo:
        screen._tree_text()
    assert GUARD_MESSAGE in str(excinfo.value)

    assert CYCLE_NOTICE in screen._tree_lines().plain
