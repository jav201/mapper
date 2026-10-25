"""HLR-RMG.1 -- gap detection and ranking (`mapper.relmap.gaps`).

Oracles are RE-DERIVED over the `reqharness` profile or a synthetic one, never copied from
QuickMap (`qm:test_gaps.py`).  The snapshot arm `test_snapshot_gaps` is Inc-4's (it needs the
adapter and the snapshot fixture).  NO assertion reads a clock: the ceiling mutants are killed
by the visit counter and the `down` tripwire (PDR condition D-1, ledger .32).
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from mapper.osopen import MAX_EDGES, MAX_NODES
from mapper.relmap import gaps as gapsmod
from mapper.relmap.gaps import Gap, detect_gaps, rank_gaps
from mapper.relmap.model import VISIT_BUDGET, Edge, Node, RelMap, build_map
from mapper.relmap.profile import REQHARNESS, EdgeType, GapRow, Profile

ALL = ("US", "HLR", "LLR", "AT", "TC")


def mk(nodes, edges=(), sourced=ALL, profile=REQHARNESS):
    return build_map(profile, nodes, edges, sourced=sourced)


def kinds_of(gaps):
    return [(g.kind, g.node) for g in gaps]


# ---------------------------------------------------------------- the catalogue (LLR-RMG.1.1)

CATALOGUE_KINDS = {
    "TRACEABILITY CYCLE", "US WITHOUT AT", "OPEN AT WITHOUT TEST", "VERIFIES WITHOUT EVIDENCE",
    "AT TAGGED ONLY", "LLR NOT VERIFIED", "HLR WITHOUT LLR", "ORPHAN TC",
}


def test_catalogue_is_the_eight_kinds_of_map_types_without_the_timeline_row():
    assert {g.kind for g in REQHARNESS.gaps} == CATALOGUE_KINDS
    assert len(REQHARNESS.gaps) == 8
    assert "UNDATED, CANNOT BE PLACED" not in CATALOGUE_KINDS  # R4's, timeline only


LOOPY = Profile(
    "loopy", ("X", "Y"),
    (EdgeType("xx", (("X", "X"), ("X", "Y"), ("Y", "X")), True, "none"),),
    (GapRow("LOOP", "HIGH", "cycle", None, None, None, False, False, (), "cycle of <n> nodes through <id>"),),
)


def test_cycle_positive_two_node_ring():
    m = build_map(LOOPY, [Node("a", "X"), Node("b", "Y")],
                  [Edge("a", "b", "xx"), Edge("b", "a", "xx")], sourced=())
    [g] = detect_gaps(m)
    assert (g.severity, g.kind, g.node, g.sentence, g.reach) == (
        "HIGH", "LOOP", "a", "cycle of 2 nodes through a", 0)


def test_cycle_positive_self_loop_is_a_component_of_one():
    m = build_map(LOOPY, [Node("a", "X")], [Edge("a", "a", "xx")], sourced=())
    [g] = detect_gaps(m)
    assert g.sentence == "cycle of 1 nodes through a"


def test_cycle_negative_no_cycle_no_gap():
    m = build_map(LOOPY, [Node("a", "X"), Node("b", "Y")], [Edge("a", "b", "xx")], sourced=())
    assert detect_gaps(m) == []


def test_us_without_at_positive_and_negative():
    m = mk([Node("US1", "US", "u1"), Node("US2", "US", "u2"), Node("AT1", "AT")],
           [Edge("AT1", "US2", "covers")])
    assert [(g.severity, g.kind, g.node, g.sentence) for g in detect_gaps(m)] == [
        ("HIGH", "US WITHOUT AT", "US1", "US1 has no covering AT: u1")]


def test_us_without_at_is_for_active_us_only():
    m = mk([Node("US1", "US", "u", status="deferred"), Node("AT1", "AT")])
    assert detect_gaps(m) == []


def test_open_at_without_test_positive_and_negatives():
    m = mk([Node("AT1", "AT", "a1", open=True), Node("AT2", "AT", "a2", open=False),
            Node("AT3", "AT", "a3", open=True), Node("TC1", "TC"),
            Node("AT4", "AT", "a4", open=True, status="withdrawn")],
           [Edge("AT3", "TC1", "binds")])
    assert [(g.kind, g.node, g.sentence) for g in detect_gaps(m)
            if g.kind == "OPEN AT WITHOUT TEST"] == [
        ("OPEN AT WITHOUT TEST", "AT1", "AT1 is open and bound to no test: a1")]


def test_verifies_without_evidence_positive_and_negative():
    m = mk([Node("LLR1", "LLR"), Node("TC1", "TC"), Node("TC2", "TC")],
           [Edge("TC1", "LLR1", "verifies", evidence_missing=True),
            Edge("TC2", "LLR1", "verifies", evidence_missing=False)],
           sourced=("LLR", "TC"))
    assert [(g.severity, g.kind, g.node, g.sentence) for g in detect_gaps(m)] == [
        ("HIGH", "VERIFIES WITHOUT EVIDENCE", "LLR1", "TC1 verifies LLR1 with no evidence")]


def test_at_tagged_only_positive_and_negative():
    m = mk([Node("AT1", "AT"), Node("AT2", "AT"), Node("TC1", "TC")],
           [Edge("AT1", "TC1", "binds", evidence_missing=True),
            Edge("AT2", "TC1", "binds", evidence_missing=False)],
           sourced=("AT", "TC"))
    assert [(g.severity, g.kind, g.node, g.sentence) for g in detect_gaps(m)
            if g.kind == "AT TAGGED ONLY"] == [
        ("MED", "AT TAGGED ONLY", "TC1", "AT1 is tagged to TC1 with no evidence")]


def test_llr_not_verified_positive_and_negative():
    m = mk([Node("LLR1", "LLR", "l1"), Node("LLR2", "LLR", "l2"), Node("TC1", "TC")],
           [Edge("TC1", "LLR2", "verifies")], sourced=("LLR", "TC"))
    assert [(g.severity, g.kind, g.node, g.sentence) for g in detect_gaps(m)] == [
        ("MED", "LLR NOT VERIFIED", "LLR1", "LLR1 has no verifying TC: l1")]


def test_edge_type_filter_lacks_in_other_edge_type_is_no_verifier():
    # review-inc002 F1: only an edge of the row's type links; a `refines` into an LLR is no verifier
    m = mk([Node("HLR1", "HLR"), Node("LLR1", "LLR", "l1")],
           [Edge("HLR1", "LLR1", "refines")], sourced=("HLR", "LLR", "TC"))
    assert [(g.kind, g.node, g.sentence) for g in detect_gaps(m)
            if g.kind == "LLR NOT VERIFIED"] == [
        ("LLR NOT VERIFIED", "LLR1", "LLR1 has no verifying TC: l1")]


def test_edge_type_filter_lacks_out_other_edge_type_is_no_binding():
    # counterpart for lacks_out: an open AT whose only edge is `covers` is still bound to no test
    m = mk([Node("AT1", "AT", "a1", open=True), Node("US1", "US")],
           [Edge("AT1", "US1", "covers")], sourced=("AT", "TC"))
    assert [(g.kind, g.node, g.sentence) for g in detect_gaps(m)
            if g.kind == "OPEN AT WITHOUT TEST"] == [
        ("OPEN AT WITHOUT TEST", "AT1", "AT1 is open and bound to no test: a1")]


def test_hlr_without_llr_positive_and_negative():
    m = mk([Node("HLR1", "HLR", "h1"), Node("HLR2", "HLR", "h2"), Node("LLR1", "LLR")],
           [Edge("HLR2", "LLR1", "refines")], sourced=("HLR", "LLR"))
    assert [(g.severity, g.kind, g.node, g.sentence) for g in detect_gaps(m)] == [
        ("MED", "HLR WITHOUT LLR", "HLR1", "HLR1 has no LLR under it: h1")]


def test_an_incoming_refines_does_not_count_as_a_child():
    m = mk([Node("US1", "US"), Node("HLR1", "HLR", "h1")], [Edge("US1", "HLR1", "refines")],
           sourced=("HLR", "LLR"))
    assert kinds_of(detect_gaps(m)) == [("HLR WITHOUT LLR", "HLR1")]


def test_orphan_tc_positive_and_negative_and_no_status_filter():
    m = mk([Node("TC1", "TC", "t1"), Node("TC2", "TC", "t2", status="deferred"),
            Node("TC3", "TC"), Node("LLR1", "LLR")],
           [Edge("TC3", "LLR1", "verifies")], sourced=("TC",))
    assert [(g.severity, g.kind, g.node, g.sentence) for g in detect_gaps(m)] == [
        ("LOW", "ORPHAN TC", "TC1", "TC1 verifies nothing: t1"),
        ("LOW", "ORPHAN TC", "TC2", "TC2 verifies nothing: t2")]


PEER = Profile(
    "peer", ("P", "Q", "R"), (EdgeType("e", (("P", "Q"), ("P", "R")), True, "none"),),
    (GapRow("P WITHOUT Q", "MED", "lacks_out", "P", "e", "Q", True, False, ("P", "Q"), "<id> has no Q"),),
)


def test_peer_kind_restricts_the_linking_edge():
    m = build_map(PEER, [Node("p1", "P"), Node("p2", "P"), Node("q", "Q"), Node("r", "R")],
                  [Edge("p1", "r", "e"), Edge("p2", "q", "e")], sourced=("P", "Q"))
    assert kinds_of(detect_gaps(m)) == [("P WITHOUT Q", "p1")]


def test_the_empty_map_has_no_gap():
    assert detect_gaps(mk([])) == []


def test_detection_order_is_catalogue_order_then_input_order():
    m = mk([Node("TC9", "TC", "t"), Node("HLR2", "HLR", "h2"), Node("US1", "US", "u1"),
            Node("HLR1", "HLR", "h1"), Node("TC1", "TC", "t1"), Node("LLR1", "LLR", "l")])
    assert kinds_of(detect_gaps(m)) == [
        ("US WITHOUT AT", "US1"), ("LLR NOT VERIFIED", "LLR1"),
        ("HLR WITHOUT LLR", "HLR2"), ("HLR WITHOUT LLR", "HLR1"),
        ("ORPHAN TC", "TC9"), ("ORPHAN TC", "TC1")]


def test_detect_returns_reach_zero_and_does_not_spend_the_budget():
    m = mk([Node("HLR1", "HLR"), Node("TC1", "TC")])
    assert {g.reach for g in detect_gaps(m)} == {0}
    assert m.visits == 0


# ---------------------------------------------------------------- the qualifier

QUAL = " (canon rows near this id could not be parsed or linked: {})"


def test_gap_sentence_qualified():
    m = mk([Node("HLR1", "HLR", "h1", unparsed=2), Node("HLR2", "HLR", "h2", unparsed=0),
            Node("US1", "US", "u", unparsed=1)], sourced=("HLR", "LLR", "US", "AT"))
    got = {g.node: g.sentence for g in detect_gaps(m)}
    assert got["HLR1"] == "HLR1 has no LLR under it: h1" + QUAL.format(2)
    assert got["HLR2"] == "HLR2 has no LLR under it: h2"
    assert got["US1"] == "US1 has no covering AT: u" + QUAL.format(1)


def test_the_qualifier_is_for_lacks_hits_only():
    m = mk([Node("LLR1", "LLR", unparsed=3), Node("TC1", "TC", unparsed=3)],
           [Edge("TC1", "LLR1", "verifies", evidence_missing=True)], sourced=("LLR", "TC"))
    assert detect_gaps(m)[0].sentence == "TC1 verifies LLR1 with no evidence"
    lp = build_map(LOOPY, [Node("a", "X", unparsed=5)], [Edge("a", "a", "xx")], sourced=())
    assert detect_gaps(lp)[0].sentence == "cycle of 1 nodes through a"


def test_sentence_slots_are_filled_in_one_pass():
    m = mk([Node("HLR1", "HLR", "see <id> and <n>")], sourced=("HLR", "LLR"))
    assert detect_gaps(m)[0].sentence == "HLR1 has no LLR under it: see <id> and <n>"
    e = mk([Node("TC<dst>", "TC"), Node("LLR1", "LLR")],
           [Edge("TC<dst>", "LLR1", "verifies", evidence_missing=True)], sourced=("LLR", "TC"))
    assert detect_gaps(e)[0].sentence == "TC<dst> verifies LLR1 with no evidence"


# ---------------------------------------------------------------- LLR-RMG.1.2 activation, eligibility


def test_unsourced_kind_is_silent():
    nodes = [Node("US1", "US", "u"), Node("HLR1", "HLR", "h")]
    only_hlr_llr = mk(nodes, sourced=("HLR", "LLR"))
    assert kinds_of(detect_gaps(only_hlr_llr)) == [("HLR WITHOUT LLR", "HLR1")]
    assert detect_gaps(mk(nodes, sourced=("HLR",))) == []  # LLR unsourced: HLR WITHOUT LLR is silent
    assert detect_gaps(mk(nodes, sourced=())) == []
    assert ("US WITHOUT AT", "US1") in kinds_of(detect_gaps(mk(nodes, sourced=("US", "AT"))))


@pytest.mark.parametrize("status", ["deferred", "superseded", "withdrawn", "split", "", "Active", "bogus"])
def test_retired_node_not_reported_but_traversed(status):
    m = mk([Node("US1", "US", status=status), Node("HLR1", "HLR", status=status),
            Node("LLR1", "LLR")], [Edge("US1", "HLR1", "refines")],
           sourced=("US", "HLR", "LLR", "AT"))
    assert kinds_of(detect_gaps(m)) == []
    assert m.reach("US1") == 1 and m.up("HLR1") == ("US1",)


def test_an_active_node_is_reported_where_the_retired_one_is_not():
    m = mk([Node("HLR1", "HLR", status="withdrawn"), Node("HLR2", "HLR", status="active")],
           sourced=("HLR", "LLR"))
    assert kinds_of(detect_gaps(m)) == [("HLR WITHOUT LLR", "HLR2")]


def test_withdrawn_only_llr_is_not_a_gap():
    m = mk([Node("HLR1", "HLR"), Node("LLR1", "LLR", status="withdrawn")],
           [Edge("HLR1", "LLR1", "refines")], sourced=("HLR", "LLR"))
    assert detect_gaps(m) == []


def test_a_map_with_no_hlr_has_no_hlr_without_llr_gap():
    assert detect_gaps(mk([Node("LLR1", "LLR")], sourced=("HLR", "LLR"))) == []


# ---------------------------------------------------------------- LLR-RMG.1.3 ranking

CHAIN = Profile("chain", ("N",), (EdgeType("next", (("N", "N"),), True, "none"),), ())


def tail(prefix, count):
    """`prefix` plus `count` descendants in a chain: reach(prefix) == count."""
    ids = [prefix] + [f"{prefix}.{i}" for i in range(count)]
    return ([Node(i, "N") for i in ids],
            [Edge(a, b, "next") for a, b in zip(ids, ids[1:])])


def chain_map(*specs):
    nodes, edges = [], []
    for prefix, count in specs:
        n, e = tail(prefix, count)
        nodes += n
        edges += e
    return build_map(CHAIN, nodes, edges, sourced=("N",))


def test_ranking():
    m = chain_map(("x", 5), ("h", 0), ("y", 9))
    found = [Gap("MED", "k", "x", "", 0), Gap("HIGH", "k", "h", "", 0), Gap("MED", "k", "y", "", 0)]
    ranked, missing = rank_gaps(m, found, None)
    assert [(g.severity, g.node, g.reach) for g in ranked] == [
        ("HIGH", "h", 0), ("MED", "y", 9), ("MED", "x", 5)]
    assert missing == 0
    assert [g.node for g in found] == ["x", "h", "y"] and {g.reach for g in found} == {0}


def test_ranking_severity_beats_reach_and_ties_keep_detection_order():
    m = chain_map(("a", 4), ("b", 4), ("c", 4), ("low", 50))
    found = [Gap("LOW", "k", "low", "", 0), Gap("MED", "k", "b", "", 0),
             Gap("MED", "k", "a", "", 0), Gap("HIGH", "k", "c", "", 0)]
    ranked, _ = rank_gaps(m, found, None)
    assert [g.node for g in ranked] == ["c", "b", "a", "low"]


def test_ranking_follows_the_catalogue_severities():
    m = mk([Node("TC1", "TC", "t"), Node("HLR1", "HLR", "h"), Node("US1", "US", "u"),
            Node("LLR1", "LLR", "l")])
    ranked, _ = rank_gaps(m, detect_gaps(m), None)
    assert [(g.severity, g.kind) for g in ranked] == [
        ("HIGH", "US WITHOUT AT"), ("MED", "LLR NOT VERIFIED"),
        ("MED", "HLR WITHOUT LLR"), ("LOW", "ORPHAN TC")]


def test_cycle_gap_reach_goes_through_the_first_member():
    nodes = [Node("a", "X"), Node("b", "Y"), Node("z", "X")]
    edges = [Edge("a", "b", "xx"), Edge("b", "a", "xx"), Edge("b", "z", "xx")]
    m = build_map(LOOPY, nodes, edges, sourced=())
    [g], missing = rank_gaps(m, detect_gaps(m), None)
    assert g.node == "a" and g.reach == m.reach("a") == 2 and missing == 0


def test_rank_computes_reach_only_for_the_bands_needed_to_fill_the_limit():
    m = chain_map(("h1", 10), ("h2", 10), ("m1", 10), ("l1", 10))
    found = [Gap("LOW", "k", "l1", "", 0), Gap("MED", "k", "m1", "", 0),
             Gap("HIGH", "k", "h1", "", 0), Gap("HIGH", "k", "h2", "", 0)]
    ranked, _ = rank_gaps(m, found, 2)   # the two HIGH gaps fill the limit
    assert m.visits == 2 * 11
    assert [(g.node, g.reach) for g in ranked] == [("h1", 10), ("h2", 10), ("m1", 0), ("l1", 0)]
    m2 = chain_map(("h1", 10), ("m1", 10), ("l1", 10))
    rank_gaps(m2, found[:3], 2)   # HIGH + MED needed, LOW not
    assert m2.visits == 2 * 11
    m3 = chain_map(("h1", 10), ("m1", 10), ("l1", 10))
    ranked3, _ = rank_gaps(m3, found[:3], 0)
    assert m3.visits == 0 and {g.reach for g in ranked3} == {0}


def test_rank_limit_none_ranks_every_band():
    m = chain_map(("h1", 3), ("m1", 4), ("l1", 5))
    found = [Gap("LOW", "k", "l1", "", 0), Gap("MED", "k", "m1", "", 0), Gap("HIGH", "k", "h1", "", 0)]
    ranked, missing = rank_gaps(m, found, None)
    assert [(g.node, g.reach) for g in ranked] == [("h1", 3), ("m1", 4), ("l1", 5)] and missing == 0
    assert m.visits == 4 + 5 + 6


HUB = Profile(
    "hub", ("N",), (EdgeType("next", (("N", "N"),), True, "none"),),
    (GapRow("NO PARENT", "HIGH", "lacks_in", "N", "next", None, False, False, ("N",), "<id> has no parent"),),
)


def hub_map(gap_nodes, chain_len):
    head = [f"c{i}" for i in range(chain_len)]
    nodes = [Node(f"g{i}", "N") for i in range(gap_nodes)] + [Node(c, "N") for c in head]
    edges = [Edge(f"g{i}", head[0], "next") for i in range(gap_nodes)]
    edges += [Edge(a, b, "next") for a, b in zip(head, head[1:])]
    return build_map(HUB, nodes, edges, sourced=("N",))


def tripwire(monkeypatch):
    calls = {"n": 0}
    real = RelMap.down

    def counting_down(self, nid):
        calls["n"] += 1
        assert calls["n"] <= VISIT_BUDGET, "tripwire: more node expansions than the budget"
        return real(self, nid)

    monkeypatch.setattr(RelMap, "down", counting_down)
    return calls


def test_rank_visit_cap(monkeypatch):
    m = hub_map(50_000, 49_990)
    assert 50_000 + 49_990 <= MAX_NODES and 50_000 + 49_989 <= MAX_EDGES
    found = detect_gaps(m)
    assert len(found) == 50_000
    calls = tripwire(monkeypatch)
    ranked, missing = rank_gaps(m, found, 20)
    assert m.visits <= VISIT_BUDGET and calls["n"] <= VISIT_BUDGET
    assert missing > 0
    assert len(ranked) == 50_000
    assert ranked[0].reach == 49_990                      # the first rows were computed
    assert ranked[-1].reach == 0                          # an uncomputed row ranks with reach 0
    assert sum(1 for g in ranked if g.reach == 0) == missing


def test_rank_limit_none_stays_inside_the_budget(monkeypatch):
    m = hub_map(50_000, 49_990)
    found = [Gap("LOW" if i % 2 else "HIGH", "k", g.node, "", 0) for i, g in enumerate(detect_gaps(m))]
    calls = tripwire(monkeypatch)
    ranked, missing = rank_gaps(m, found, None)
    assert m.visits <= VISIT_BUDGET and calls["n"] <= VISIT_BUDGET
    assert missing > 0 and len(ranked) == 50_000


def test_rank_100k_sinks():
    m = build_map(HUB, [Node(f"s{i}", "N") for i in range(MAX_NODES)], [], sourced=("N",))
    ranked, missing = rank_gaps(m, detect_gaps(m), None)
    assert len(ranked) == MAX_NODES and missing == 0 and m.visits <= VISIT_BUDGET
    assert {g.reach for g in ranked} == {0}


def test_rank_shares_the_budget_with_reach_calls_made_elsewhere():
    m = hub_map(60, 49_990)
    for i in range(60):
        m.reach(f"g{i}")                                  # a view spends the same budget
    assert 40 * 49_991 <= m.visits <= VISIT_BUDGET
    spent = m.visits
    ranked, missing = rank_gaps(m, [Gap("HIGH", "k", "g59", "", 0)], None)
    assert m.visits >= spent                              # never reset by ranking
    assert (ranked[0].reach, missing) in {(49_990, 0), (0, 1)}


# ---------------------------------------------------------------- generic and counted-only


GAPS_PY = Path(gapsmod.__file__)
ADJACENCY = {"down", "up", "_down", "_up", "_reach_memo", "_visits", "neighbourhood"}


def adjacency_reads(source: str) -> list[str]:
    return sorted({n.attr for n in ast.walk(ast.parse(source))
                   if isinstance(n, ast.Attribute) and n.attr in ADJACENCY})


def test_gaps_reads_no_adjacency_itself():
    assert adjacency_reads(GAPS_PY.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize("planted", ["down", "up", "_down", "_reach_memo", "_visits", "neighbourhood"])
def test_the_adjacency_census_finds_a_planted_read(planted):
    assert adjacency_reads(f"def f(m):\n    return m.{planted}\n") == [planted]


def test_gaps_module_names_nothing_of_the_profile():
    from tests.test_relmap_isolation import engine_literal_violations, profile_literals
    assert engine_literal_violations(GAPS_PY.read_text(encoding="utf-8"), profile_literals(REQHARNESS)) == []


def test_the_engine_is_generic_over_any_catalogue():
    other = Profile(
        "other", ("A", "B"), (EdgeType("rel", (("A", "B"),), True, "none"),),
        (GapRow("A ALONE", "LOW", "lacks_out", "A", "rel", None, False, False, ("A",), "<id> alone"),
         GapRow("B ALONE", "HIGH", "lacks_in", "B", "rel", None, False, False, ("B",), "<id> alone")),
    )
    m = build_map(other, [Node("a", "A"), Node("b", "B")], [], sourced=("A", "B"))
    ranked, _ = rank_gaps(m, detect_gaps(m), None)
    assert [(g.severity, g.kind, g.node) for g in ranked] == [("HIGH", "B ALONE", "b"), ("LOW", "A ALONE", "a")]


def test_a_slot_the_pattern_does_not_supply_stays_as_text():
    # review-inc002 F3: `<src>` is an edge-row slot; a lacks_* row naming it keeps it literally
    prof = Profile(
        "slot", ("P",), (EdgeType("e", (("P", "P"),), True, "none"),),
        (GapRow("P ALONE", "MED", "lacks_out", "P", "e", None, False, False, ("P",), "<id> uses <src>"),),
    )
    m = build_map(prof, [Node("p1", "P")], [], sourced=("P",))
    assert detect_gaps(m)[0].sentence == "p1 uses <src>"
