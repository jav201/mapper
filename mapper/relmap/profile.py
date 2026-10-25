"""The relation-map PROFILE: node kinds, edge types and the gap catalogue, as data.

The engine (`model`, and `gaps` later) names no node kind, edge type or gap kind except
through the `Profile` it is given (LLR-RMP.1.2); everything a profile says lives in the
tables below.  `REQHARNESS` is the only profile R1 ships (`lineage` is R5).

This module is the leaf of the package: it imports nothing from `mapper`.

Direction of change.  `EdgeType.downstream` is True when a change at the edge's `src`
flows to its `dst` (`refines`); otherwise a change at `dst` flows to `src` (`covers`,
`verifies`, `binds` -- the AT and the TC sit downstream of what they check).  This is the
NORMATIVE rule of MAP-TYPES, which the section-3.2 prose on `binds` contradicts (premise 6).

Gap patterns are a closed set of four (`PATTERNS`); a catalogue row names one and the
kinds and edge it applies to.  Sentence templates keep their `<placeholders>` -- the
detector fills them in.
"""
from __future__ import annotations

from dataclasses import dataclass

PATTERNS = ("cycle", "lacks_in", "lacks_out", "edge_unevidenced")
SEVERITIES = ("HIGH", "MED", "LOW")


@dataclass(frozen=True)
class EdgeType:
    """One edge type: the (src kind, dst kind) pairs it may join, its direction and its evidence rule."""

    name: str
    pairs: tuple[tuple[str, str], ...]
    downstream: bool
    evidence: str  # "none" | "optional" | "required" | "graduated"


@dataclass(frozen=True)
class GapRow:
    """One row of the gap catalogue.

    `eligible`: only nodes whose status is `active` can be reported.  `open`: only nodes
    whose `open` field is true.  `needs`: node kinds that must be SOURCED before the row
    can fire at all (an unsourced kind produces no gap -- an honest partial map).
    """

    kind: str
    severity: str
    pattern: str
    node_kind: str | None
    edge: str | None
    peer: str | None
    eligible: bool
    open: bool
    needs: tuple[str, ...]
    sentence: str


@dataclass(frozen=True)
class Profile:
    name: str
    node_kinds: tuple[str, ...]
    edge_types: tuple[EdgeType, ...]
    gaps: tuple[GapRow, ...]

    def __post_init__(self) -> None:
        kinds = set(self.node_kinds)
        edges = {t.name for t in self.edge_types}
        for t in self.edge_types:
            for src, dst in t.pairs:
                if src not in kinds or dst not in kinds:
                    raise ValueError(f"edge type {t.name!r} joins a kind outside the profile")
        for g in self.gaps:
            named = [g.node_kind, g.peer, *g.needs]
            if any(k is not None and k not in kinds for k in named):
                raise ValueError(f"gap {g.kind!r} names a kind outside the profile")
            if g.edge is not None and g.edge not in edges:
                raise ValueError(f"gap {g.kind!r} names an edge type outside the profile")
            if g.pattern not in PATTERNS:
                raise ValueError(f"gap {g.kind!r} uses a pattern outside the closed set")
            if g.severity not in SEVERITIES:
                raise ValueError(f"gap {g.kind!r} has a severity outside the closed set")


REQHARNESS = Profile(
    name="reqharness",
    node_kinds=("US", "HLR", "LLR", "AT", "TC"),
    edge_types=(
        EdgeType("refines", (("US", "HLR"), ("HLR", "LLR")), True, "none"),
        EdgeType("covers", (("AT", "US"),), False, "optional"),
        EdgeType("verifies", (("TC", "LLR"), ("TC", "HLR")), False, "required"),
        EdgeType("binds", (("AT", "TC"),), False, "graduated"),
    ),
    gaps=(
        GapRow("TRACEABILITY CYCLE", "HIGH", "cycle", None, None, None, False, False, (),
               "cycle of <n> nodes through <id>"),
        GapRow("US WITHOUT AT", "HIGH", "lacks_in", "US", "covers", None, True, False,
               ("US", "AT"), "<id> has no covering AT: <title>"),
        GapRow("OPEN AT WITHOUT TEST", "HIGH", "lacks_out", "AT", "binds", None, True, True,
               ("AT", "TC"), "<id> is open and bound to no test: <title>"),
        GapRow("VERIFIES WITHOUT EVIDENCE", "HIGH", "edge_unevidenced", None, "verifies", None,
               False, False, ("TC",), "<src> verifies <dst> with no evidence"),
        GapRow("AT TAGGED ONLY", "MED", "edge_unevidenced", None, "binds", None, False, False,
               ("AT", "TC"), "<src> is tagged to <dst> with no evidence"),
        GapRow("LLR NOT VERIFIED", "MED", "lacks_in", "LLR", "verifies", None, True, False,
               ("LLR", "TC"), "<id> has no verifying TC: <title>"),
        GapRow("HLR WITHOUT LLR", "MED", "lacks_out", "HLR", "refines", "LLR", True, False,
               ("HLR", "LLR"), "<id> has no LLR under it: <title>"),
        GapRow("ORPHAN TC", "LOW", "lacks_out", "TC", "verifies", None, False, False,
               ("TC",), "<id> verifies nothing: <title>"),
    ),
)
