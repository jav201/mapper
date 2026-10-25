"""HLR-RMM.1 / RMM.2 / RMM.3 -- the typed multi-parent read model (`mapper.relmap.model`).

Oracles are RE-DERIVED over the `reqharness` profile or a synthetic one, never copied from
QuickMap (`qm:test_model.py`, lineage-shaped).  The heavy shapes (100,000-node chain, the
cap +-1 arms) live in their own functions so a failure names the shape, and NO assertion
reads a clock: the ceiling mutants are killed by the visit counter and the `down` tripwire
(PDR condition D-1, ledger .32).
"""
from __future__ import annotations

import dataclasses

import pytest

from mapper.osopen import MAX_EDGES, MAX_NODES
from mapper.relmap import model as relmodel
from mapper.relmap.model import (
    DISPLAY_MAX,
    VISIT_BUDGET,
    Edge,
    Node,
    Problem,
    RelMap,
    RelMapLimitError,
    build_map,
    cut,
)
from mapper.relmap.profile import REQHARNESS, EdgeType, Profile

CHAIN = Profile("chain", ("N",), (EdgeType("next", (("N", "N"),), True, "none"),), ())
LOOPY = Profile(
    "loopy", ("X", "Y"),
    (EdgeType("xx", (("X", "X"), ("X", "Y"), ("Y", "X")), True, "none"),), ())


def _n(i):
    return Node(f"n{i}", "N")


def _chain(count):
    nodes = [_n(i) for i in range(count)]
    edges = [Edge(f"n{i}", f"n{i + 1}", "next") for i in range(count - 1)]
    return build_map(CHAIN, nodes, edges, sourced={"N"})


def _closure(m, start):
    """Independent reachability through `down` (a test-side walk, not the code under test)."""
    seen, todo = set(), [start]
    while todo:
        for nxt in m.down(todo.pop()):
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    return seen - {start}


# ---------------------------------------------------------------- LLR-RMM.1.1


def test_value_defaults():
    n = Node("x", "LLR")
    assert (n.title, n.status, n.open, n.unparsed) == ("", "active", False, 0)
    e = Edge("a", "b", "refines")
    assert (e.evidence_missing, e.in_cycle) == (False, False)
    p = Problem("duplicate id", "x")
    assert (p.kind, p.subject) == ("duplicate id", "x")
    for value in (n, e, p):
        with pytest.raises(dataclasses.FrozenInstanceError):
            setattr(value, dataclasses.fields(value)[0].name, "changed")


def test_multi_parent_and_order():
    nodes = [Node("TC9", "TC"), Node("LLR2", "LLR"), Node("HLR1", "HLR"), Node("LLR1", "LLR")]
    edges = [
        Edge("TC9", "LLR2", "verifies"),
        Edge("TC9", "HLR1", "verifies"),
        Edge("TC9", "LLR1", "verifies"),
        Edge("HLR1", "LLR1", "refines"),
    ]
    m = build_map(REQHARNESS, nodes, edges, sourced={"TC", "LLR", "HLR"})
    assert [n.id for n in m.nodes] == ["TC9", "LLR2", "HLR1", "LLR1"]
    assert m.edges == tuple(edges)
    assert isinstance(m.nodes, tuple) and isinstance(m.edges, tuple)
    # TC9 verifies three things: three parents, all kept (change at each reaches TC9).
    assert m.up("TC9") == ("LLR2", "HLR1", "LLR1")
    assert m.up("LLR1") == ("HLR1",)
    assert m.problems == ()
    assert m.node("HLR1") == nodes[2]
    assert m.node("nope") is None
    assert m.profile is REQHARNESS
    assert m.sourced == frozenset({"TC", "LLR", "HLR"})


def test_empty_lists():
    m = build_map(CHAIN, [], [], sourced=())
    assert (m.nodes, m.edges, m.problems, m.cycles) == ((), (), (), ())
    assert (m.reach("x"), m.up("x"), m.down("x"), m.neighbourhood("x", 3)) == (
        0, (), (), frozenset())


# ---------------------------------------------------------------- LLR-RMM.1.2


def _kinds(m):
    return [p.kind for p in m.problems]


def test_problem_duplicate_id():
    m = build_map(CHAIN, [Node("a", "N", title="first"), Node("a", "N", title="later")], [],
                  sourced={"N"})
    assert _kinds(m) == ["duplicate id"]
    assert [n.title for n in m.nodes] == ["first"]
    assert m.problems[0].subject == "a"


@pytest.mark.parametrize(
    "bad_id",
    ["", "x" * 201, "a\x1bb", "a\u202eb", "a\u200bb", "a\u2028b", "a\nb", "a\x7fb"],
    ids=["empty", "len201", "esc", "u202e", "u200b", "u2028", "newline", "del"],
)
def test_problem_unsafe_id(bad_id):
    m = build_map(CHAIN, [Node(bad_id, "N"), Node("ok", "N")], [], sourced={"N"})
    assert _kinds(m) == ["unsafe id"]
    assert [n.id for n in m.nodes] == ["ok"]


def test_problem_unsafe_id_boundary_200_is_safe():
    m = build_map(CHAIN, [Node("x" * 200, "N")], [], sourced={"N"})
    assert m.problems == () and len(m.nodes) == 1


def test_problem_unknown_node_kind():
    m = build_map(CHAIN, [Node("a", "N"), Node("b", "Z")], [], sourced={"N"})
    assert _kinds(m) == ["unknown node kind"]
    assert [n.id for n in m.nodes] == ["a"]


def test_problem_unknown_edge_type():
    m = build_map(CHAIN, [_n(0), _n(1)], [Edge("n0", "n1", "bogus")], sourced={"N"})
    assert _kinds(m) == ["unknown edge type"]
    assert m.edges == () and m.down("n0") == ()


def test_problem_unknown_endpoint():
    edges = [Edge("n0", "ghost", "next"), Edge("ghost", "n0", "next")]
    m = build_map(CHAIN, [_n(0)], edges, sourced={"N"})
    assert _kinds(m) == ["unknown endpoint", "unknown endpoint"]
    assert m.edges == ()


def test_problem_unknown_endpoint_names_an_excluded_node_as_unknown():
    # `b` is excluded (unknown kind), so an edge to it has an endpoint that is not an accepted node.
    m = build_map(CHAIN, [_n(0), Node("b", "Z")], [Edge("n0", "b", "next")], sourced={"N"})
    assert _kinds(m) == ["unknown node kind", "unknown endpoint"]


def test_problem_disallowed_pair():
    nodes = [Node("US1", "US"), Node("LLR1", "LLR")]
    m = build_map(REQHARNESS, nodes, [Edge("US1", "LLR1", "refines")], sourced={"US", "LLR"})
    assert _kinds(m) == ["disallowed pair"]
    assert m.edges == () and m.down("US1") == ()


def test_problem_mixed_input_yields_six_and_keeps_the_valid_remainder():
    nodes = [
        Node("US1", "US"), Node("HLR1", "HLR"), Node("LLR1", "LLR"),
        Node("HLR1", "HLR"),  # duplicate id
        Node("", "LLR"),  # unsafe id
        Node("Q1", "ZZ"),  # unknown node kind
    ]
    edges = [
        Edge("US1", "HLR1", "refines"),  # valid
        Edge("HLR1", "LLR1", "refines"),  # valid
        Edge("US1", "LLR1", "wat"),  # unknown edge type
        Edge("US1", "GHOST", "refines"),  # unknown endpoint
        Edge("LLR1", "US1", "refines"),  # disallowed pair
    ]
    m = build_map(REQHARNESS, nodes, edges, sourced={"US", "HLR", "LLR"})
    assert sorted(_kinds(m)) == sorted([
        "duplicate id", "unsafe id", "unknown node kind",
        "unknown edge type", "unknown endpoint", "disallowed pair"])
    assert len(m.problems) == 6
    assert [n.id for n in m.nodes] == ["US1", "HLR1", "LLR1"]
    assert [(e.src, e.dst) for e in m.edges] == [("US1", "HLR1"), ("HLR1", "LLR1")]
    assert m.reach("US1") == 2


# ---------------------------------------------------------------- LLR-RMM.1.3


def test_caps_constants_are_read_from_osopen():
    assert relmodel.MAX_NODES is MAX_NODES and relmodel.MAX_EDGES is MAX_EDGES
    assert (MAX_NODES, MAX_EDGES) == (100_000, 100_000)


def test_caps_nodes_at_cap_load_and_cap_plus_one_refuses():
    nodes = [Node(f"n{i}", "N") for i in range(MAX_NODES)]
    assert len(build_map(CHAIN, nodes, [], sourced=()).nodes) == MAX_NODES
    nodes.append(Node("extra", "N"))
    with pytest.raises(RelMapLimitError) as err:
        build_map(CHAIN, nodes, [], sourced=())
    assert str(MAX_NODES) in str(err.value)


def test_caps_edges_at_cap_load_and_cap_plus_one_refuses():
    nodes = [_n(0), _n(1)]
    edges = [Edge("n0", "n1", "next")] * MAX_EDGES
    assert len(build_map(CHAIN, nodes, edges, sourced=()).edges) == MAX_EDGES
    with pytest.raises(RelMapLimitError) as err:
        build_map(CHAIN, nodes, edges + [Edge("n0", "n1", "next")], sourced=())
    assert str(MAX_EDGES) in str(err.value)


def test_caps_refuse_before_any_validation_work():
    # Over the node cap AND every node invalid: still the limit error, not 100,001 problems.
    nodes = [Node("", "N")] * (MAX_NODES + 1)
    with pytest.raises(RelMapLimitError):
        build_map(CHAIN, nodes, [], sourced=())


# ---------------------------------------------------------------- LLR-RMM.2.1


def _flip(profile, name, downstream):
    types = tuple(
        dataclasses.replace(t, downstream=downstream) if t.name == name else t
        for t in profile.edge_types)
    return dataclasses.replace(profile, edge_types=types)


# one valid (src, dst) endpoint pair per edge type of the reqharness profile
_ENDS = {
    "refines": (("US", "US1"), ("HLR", "HLR1")),
    "covers": (("AT", "AT1"), ("US", "US1")),
    "verifies": (("TC", "TC1"), ("LLR", "LLR1")),
    "binds": (("AT", "AT1"), ("TC", "TC1")),
}


@pytest.mark.parametrize("etype", sorted(_ENDS))
@pytest.mark.parametrize("downstream", [True, False])
def test_direction_per_edge_type(etype, downstream):
    (sk, sid), (dk, did) = _ENDS[etype]
    profile = _flip(REQHARNESS, etype, downstream)
    m = build_map(profile, [Node(sid, sk), Node(did, dk)], [Edge(sid, did, etype)],
                  sourced={sk, dk})
    assert m.problems == ()
    if downstream:
        assert (m.down(sid), m.up(did), m.down(did), m.up(sid)) == ((did,), (sid,), (), ())
    else:
        assert (m.down(did), m.up(sid), m.down(sid), m.up(did)) == ((sid,), (did,), (), ())


def _premise_six():
    nodes = [Node("US1", "US"), Node("HLR1", "HLR"), Node("LLR1", "LLR"),
             Node("AT1", "AT"), Node("TC1", "TC")]
    edges = [
        Edge("US1", "HLR1", "refines"), Edge("HLR1", "LLR1", "refines"),
        Edge("AT1", "US1", "covers"), Edge("TC1", "LLR1", "verifies"),
        Edge("AT1", "TC1", "binds"),
    ]
    return build_map(REQHARNESS, nodes, edges, sourced={"US", "HLR", "LLR", "AT", "TC"})


def test_direction_premise_six_figures_on_the_reqharness_profile():
    m = _premise_six()
    assert m.problems == ()
    assert _closure(m, "LLR1") == {"AT1", "TC1"}
    assert _closure(m, "US1") == {"AT1", "HLR1", "LLR1", "TC1"}
    assert (m.reach("LLR1"), m.reach("US1")) == (2, 4)
    # an AT's change reaches nothing downstream: `binds` and `covers` run toward the AT.
    assert _closure(m, "AT1") == set()


# ---------------------------------------------------------------- LLR-RMM.2.2


def test_up_and_down_follow_edge_input_order():
    nodes = [_n(0), _n(1), _n(2), _n(3)]
    edges = [Edge("n0", "n3", "next"), Edge("n0", "n1", "next"), Edge("n0", "n2", "next")]
    m = build_map(CHAIN, nodes, edges, sourced=())
    assert m.down("n0") == ("n3", "n1", "n2")
    assert m.up("n3") == ("n0",)
    assert isinstance(m.down("n0"), tuple) and isinstance(m.up("n3"), tuple)


def test_reach_diamond_counts_nodes_not_paths():
    nodes = [Node(c, "N") for c in "abcd"]
    edges = [Edge("a", "b", "next"), Edge("a", "c", "next"),
             Edge("b", "d", "next"), Edge("c", "d", "next")]
    m = build_map(CHAIN, nodes, edges, sourced=())
    assert m.reach("a") == 3
    assert (m.reach("b"), m.reach("d")) == (1, 0)


def test_reach_isolated_and_unknown_are_zero():
    m = build_map(CHAIN, [_n(0)], [], sourced=())
    assert m.reach("n0") == 0
    assert m.reach("nope") == 0


def test_reach_in_a_cycle_excludes_self():
    m = build_map(LOOPY, [Node("a", "X"), Node("b", "X")],
                  [Edge("a", "b", "xx"), Edge("b", "a", "xx")], sourced=())
    assert (m.reach("a"), m.reach("b")) == (1, 1)
    solo = build_map(LOOPY, [Node("a", "X")], [Edge("a", "a", "xx")], sourced=())
    assert solo.reach("a") == 0


def test_neighbourhood_hops():
    m = _chain(5)  # n0 -> n1 -> n2 -> n3 -> n4
    assert m.neighbourhood("n2", 0) == frozenset({"n2"})
    assert m.neighbourhood("n2", 1) == frozenset({"n1", "n2", "n3"})
    assert m.neighbourhood("n2", 2) == frozenset({"n0", "n1", "n2", "n3", "n4"})
    assert m.neighbourhood("n2", 99) == frozenset({"n0", "n1", "n2", "n3", "n4"})
    assert isinstance(m.neighbourhood("n2", 1), frozenset)


def test_neighbourhood_walks_up_and_down_and_defines_unknown():
    m = _premise_six()
    # one hop from TC1 is its up (LLR1) and its down (AT1)
    assert m.neighbourhood("TC1", 1) == frozenset({"TC1", "LLR1", "AT1"})
    assert m.neighbourhood("nope", 2) == frozenset()


def test_queries_leave_the_graph_unchanged():
    m = _premise_six()
    before = (m.nodes, m.edges, m.problems, m.cycles, m.sourced, m.profile)
    for nid in ("US1", "AT1", "ghost"):
        m.up(nid), m.down(nid), m.reach(nid), m.neighbourhood(nid, 2)
    assert (m.nodes, m.edges, m.problems, m.cycles, m.sourced, m.profile) == before
    for attr in ("nodes", "edges", "problems", "cycles", "sourced", "profile", "visits"):
        with pytest.raises(AttributeError):
            setattr(m, attr, None)
    with pytest.raises(AttributeError):
        m.extra = 1  # no instance dict to grow


def test_reach_chain_at_cap_has_no_recursion_error():
    m = _chain(MAX_NODES)
    assert m.reach("n0") == MAX_NODES - 1  # 99,999


def test_neighbourhood_chain_at_cap_has_no_recursion_error():
    m = _chain(MAX_NODES)
    assert len(m.neighbourhood("n0", MAX_NODES)) == MAX_NODES


def test_reach_memo_is_counts():
    m = _chain(2_000)
    for i in range(0, 2_000, 7):
        assert m.reach(f"n{i}") == 1_999 - i
    memo = m._reach_memo  # the tested seam: an int per node, never a reachable set
    assert len(memo) >= 100
    assert all(type(v) is int for v in memo.values())


def test_reach_budget_per_row(monkeypatch):
    m = _chain(MAX_NODES)
    calls = {"n": 0}
    real = RelMap.down

    def counting_down(self, nid):
        calls["n"] += 1
        assert calls["n"] <= VISIT_BUDGET, "tripwire: more node expansions than the budget"
        return real(self, nid)

    monkeypatch.setattr(RelMap, "down", counting_down)
    results = [m.reach(f"n{i}") for i in range(MAX_NODES)]  # the per-row call a view makes
    assert m.visits <= VISIT_BUDGET
    assert calls["n"] <= VISIT_BUDGET
    assert None in results
    assert results[0] == MAX_NODES - 1  # the first rows were computed before the budget ran out
    assert all(r is None or isinstance(r, int) for r in results)
    # once spent, a not-yet-memoised row stays "not computed", and is never a partial count
    assert m.reach(f"n{MAX_NODES - 1}") is None


def test_reach_budget_is_the_documented_constant():
    assert VISIT_BUDGET == 2_000_000
    assert _chain(3).visits == 0


def test_reach_budget_is_one_per_map_object():
    a, b = _chain(50), _chain(50)
    a.reach("n0")
    assert a.visits > 0 and b.visits == 0


# ---------------------------------------------------------------- LLR-RMM.3.1


def test_cycle_self_loop():
    m = build_map(LOOPY, [Node("a", "X")], [Edge("a", "a", "xx")], sourced=())
    assert m.cycles == (("a",),)
    assert m.edges[0].in_cycle is True


def test_cycle_three_nodes_flags_each_cycle_edge_and_still_loads():
    nodes = [Node(c, "X") for c in "abcd"]
    edges = [Edge("a", "b", "xx"), Edge("b", "c", "xx"), Edge("c", "a", "xx"),
             Edge("c", "d", "xx")]
    m = build_map(LOOPY, nodes, edges, sourced=())
    assert m.cycles == (("a", "b", "c"),)
    assert [e.in_cycle for e in m.edges] == [True, True, True, False]
    assert m.problems == ()


def test_cycle_two_disjoint_cycles_in_node_order():
    nodes = [Node(c, "X") for c in "wxyz"]
    edges = [Edge("z", "y", "xx"), Edge("y", "z", "xx"), Edge("w", "x", "xx"),
             Edge("x", "w", "xx")]
    m = build_map(LOOPY, nodes, edges, sourced=())
    assert m.cycles == (("w", "x"), ("y", "z"))
    assert all(e.in_cycle for e in m.edges)


def test_cycle_acyclic_reports_none_and_clears_a_caller_supplied_flag():
    nodes = [Node("a", "X"), Node("b", "X")]
    m = build_map(LOOPY, nodes, [Edge("a", "b", "xx", in_cycle=True)], sourced=())
    assert m.cycles == ()
    assert m.edges[0].in_cycle is False  # set by the builder only


def test_cycle_edge_between_two_cycles_is_not_in_a_cycle():
    nodes = [Node(c, "X") for c in "abcd"]
    edges = [Edge("a", "b", "xx"), Edge("b", "a", "xx"), Edge("b", "c", "xx"),
             Edge("c", "d", "xx"), Edge("d", "c", "xx")]
    m = build_map(LOOPY, nodes, edges, sourced=())
    assert len(m.cycles) == 2
    assert [e.in_cycle for e in m.edges] == [True, True, False, True, True]


def test_cycle_deep_chain_has_no_cycle_and_no_recursion_error():
    assert _chain(MAX_NODES).cycles == ()


def test_cycle_deep_ring_is_one_component_and_no_recursion_error():
    count = MAX_NODES
    nodes = [_n(i) for i in range(count)]
    edges = [Edge(f"n{i}", f"n{(i + 1) % count}", "next") for i in range(count)]
    m = build_map(CHAIN, nodes, edges, sourced=())
    assert len(m.cycles) == 1 and len(m.cycles[0]) == count and m.cycles[0][0] == "n0"
    assert all(e.in_cycle for e in m.edges)


# ---------------------------------------------------------------- DISPLAY_MAX / cut


def test_cut_boundary_120_and_121():
    assert DISPLAY_MAX == 120
    assert cut("") == ""
    assert cut("a" * 120) == "a" * 120
    cut121 = cut("a" * 121)
    assert len(cut121) == 120 and cut121.endswith("…") and cut121[:-1] == "a" * 119
    assert len(cut("b" * 1_000_000)) == 120
