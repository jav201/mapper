"""HLR-RMP.1 / LLR-RMP.1.1 -- the `reqharness` profile is a table, and the table is exactly this one.

The expected values below are typed from the contract's two tables (`01-requirements.md`
LLR-RMP.1.1), NOT derived from `REQHARNESS`: a derivation would agree with a wrong table
(C-31).  Cell by cell, so a flipped direction or a changed severity names its own cell.
"""
from __future__ import annotations

import dataclasses

import pytest

from mapper.relmap.profile import REQHARNESS, EdgeType, GapRow, Profile

# (name, ((src, dst), ...), downstream, evidence)
EXPECTED_EDGES = (
    ("refines", (("US", "HLR"), ("HLR", "LLR")), True, "none"),
    ("covers", (("AT", "US"),), False, "optional"),
    ("verifies", (("TC", "LLR"), ("TC", "HLR")), False, "required"),
    ("binds", (("AT", "TC"),), False, "graduated"),
)

# (kind, severity, pattern, node_kind, edge, peer, eligible, open, needs, sentence)
EXPECTED_GAPS = (
    ("TRACEABILITY CYCLE", "HIGH", "cycle", None, None, None, False, False, (),
     "cycle of <n> nodes through <id>"),
    ("US WITHOUT AT", "HIGH", "lacks_in", "US", "covers", None, True, False, ("US", "AT"),
     "<id> has no covering AT: <title>"),
    ("OPEN AT WITHOUT TEST", "HIGH", "lacks_out", "AT", "binds", None, True, True, ("AT", "TC"),
     "<id> is open and bound to no test: <title>"),
    ("VERIFIES WITHOUT EVIDENCE", "HIGH", "edge_unevidenced", None, "verifies", None, False,
     False, ("TC",), "<src> verifies <dst> with no evidence"),
    ("AT TAGGED ONLY", "MED", "edge_unevidenced", None, "binds", None, False, False,
     ("AT", "TC"), "<src> is tagged to <dst> with no evidence"),
    ("LLR NOT VERIFIED", "MED", "lacks_in", "LLR", "verifies", None, True, False,
     ("LLR", "TC"), "<id> has no verifying TC: <title>"),
    ("HLR WITHOUT LLR", "MED", "lacks_out", "HLR", "refines", "LLR", True, False,
     ("HLR", "LLR"), "<id> has no LLR under it: <title>"),
    ("ORPHAN TC", "LOW", "lacks_out", "TC", "verifies", None, False, False, ("TC",),
     "<id> verifies nothing: <title>"),
)


def test_profile_identity_and_kinds():
    assert REQHARNESS.name == "reqharness"
    assert REQHARNESS.node_kinds == ("US", "HLR", "LLR", "AT", "TC")


def test_edge_table():
    got = tuple((e.name, e.pairs, e.downstream, e.evidence) for e in REQHARNESS.edge_types)
    assert got == EXPECTED_EDGES
    assert len(REQHARNESS.edge_types) == 4
    assert sum(len(e.pairs) for e in REQHARNESS.edge_types) == 6
    assert [e.downstream for e in REQHARNESS.edge_types].count(True) == 1
    assert [e.downstream for e in REQHARNESS.edge_types].count(False) == 3


def test_catalogue_table():
    got = tuple(
        (g.kind, g.severity, g.pattern, g.node_kind, g.edge, g.peer, g.eligible, g.open,
         g.needs, g.sentence)
        for g in REQHARNESS.gaps
    )
    assert got == EXPECTED_GAPS
    severities = [g.severity for g in REQHARNESS.gaps]
    assert len(severities) == 8
    assert (severities.count("HIGH"), severities.count("MED"), severities.count("LOW")) == (4, 3, 1)


def test_patterns_are_a_closed_set_of_four():
    assert {g.pattern for g in REQHARNESS.gaps} == {
        "cycle", "lacks_in", "lacks_out", "edge_unevidenced"}


@pytest.mark.parametrize("value", [REQHARNESS, REQHARNESS.edge_types[0], REQHARNESS.gaps[0]])
def test_values_are_frozen(value):
    field = dataclasses.fields(value)[0].name
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(value, field, "changed")


def _profile(**over):
    base = dict(
        name="t",
        node_kinds=("A", "B"),
        edge_types=(EdgeType("e", (("A", "B"),), True, "none"),),
        gaps=(),
    )
    base.update(over)
    return Profile(**base)


def _gap(**over):
    base = dict(kind="G", severity="LOW", pattern="lacks_in", node_kind="A", edge="e",
                peer=None, eligible=False, open=False, needs=("A",), sentence="<id>")
    base.update(over)
    return GapRow(**base)


def test_a_consistent_synthetic_profile_is_accepted():
    p = _profile(gaps=(_gap(),))
    assert p.gaps[0].kind == "G"


@pytest.mark.parametrize(
    "bad",
    [
        dict(edge_types=(EdgeType("e", (("A", "Z"),), True, "none"),)),
        dict(edge_types=(EdgeType("e", (("Z", "B"),), True, "none"),)),
        dict(gaps=(_gap(node_kind="Z"),)),
        dict(gaps=(_gap(peer="Z"),)),
        dict(gaps=(_gap(needs=("Z",)),)),
        dict(gaps=(_gap(edge="nope"),)),
        dict(gaps=(_gap(pattern="made_up"),)),
        dict(gaps=(_gap(severity="CRITICAL"),)),
    ],
    ids=["pair-dst", "pair-src", "node-kind", "peer", "needs", "edge", "pattern", "severity"],
)
def test_profile_refuses_names_outside_itself_at_construction(bad):
    with pytest.raises(ValueError):
        _profile(**bad)
