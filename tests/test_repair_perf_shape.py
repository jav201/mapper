"""LLR-PERF.1 — the honest 51-node measurement fixture, and nothing more.

**THIS FILE DELIBERATELY ASSERTS NO BUDGET, AND THAT IS THE REQUIREMENT.**

`S-18` (the mount work-budget / deadline mechanism) is PARKED by operator rider for
the `2026-08-26-ui-next-batch-02` PDR, which already carries the pre-authorised
change to the renderer contract.  The deadline hook belongs in that redesign --
designed once, not patched into three private copies of the walk.  This batch lands
the MEASUREMENT, not the CONTROL.  A fixture that asserted a time budget here would
BE the bolted-in mechanism the rider forbids, arriving through the back door of a
test file.

There is a second, independent reason not to assert a wall-clock budget here, and
this batch measured it: the existing slow lane already does, and it is ~10% flaky
under concurrent load.  `test_repair_depth.py` asserts
`FACTORY_TREE_BOUND_SECONDS = 8.0` against a walk that measures 2.6-3.4s unloaded --
2.4-3.0x headroom -- and it was driven to 10.360s simply by running another suite
alongside it.  Adding a second wall-clock assertion to the same lane would add a
second flake, not a second guarantee.

What this file DOES do is fix the shape, so the cost is reproducible when the
feature batch designs the budget against it.
"""
from __future__ import annotations

import time

import pytest

from mapper.model import Edge, Ficha, Graph, Node
from mapper.views.layered import LayeredRenderer

LAYERS = 5
PER_LAYER = 10
EXPECTED_NODES = LAYERS * PER_LAYER + 1  # 51: the layered DAG plus its root


def _layered_dag() -> Graph:
    """A 5-layer x 10-per-layer DAG: the cost shape the «sala» mount hits.

    Every node in layer N points at every node in layer N+1, so edge count grows as
    `PER_LAYER**2` per layer boundary while node count grows linearly.  That ratio
    is the point -- a chain of 51 nodes would have the same node count and none of
    the cost.
    """
    graph = Graph(root_id="root")
    graph.add_node(Node(id="root", ficha=Ficha(title="raiz")))
    previous = ["root"]
    for layer in range(LAYERS):
        current = []
        for index in range(PER_LAYER):
            nid = f"n{layer}_{index}"
            graph.add_node(Node(id=nid, ficha=Ficha(title=f"nodo {layer}.{index}")))
            current.append(nid)
        for parent in previous:
            for child in current:
                graph.edges.append(Edge(parent_id=parent, child_id=child))
        previous = current
    return graph


def test_tc_p08_the_fixture_has_the_declared_shape():
    """The shape is the deliverable, so it is asserted; the timing is not.

    Fast lane on purpose: this arm is what makes the fixture trustworthy, and it
    costs nothing.  If it lived in the slow lane it would inherit that lane's
    known flake for no reason.
    """
    graph = _layered_dag()
    assert len(graph.nodes) == EXPECTED_NODES
    # The edge count is the cost driver and is derived, not typed.
    assert len(graph.edges) == PER_LAYER + (LAYERS - 1) * PER_LAYER * PER_LAYER
    assert graph.root_id in graph.nodes


@pytest.mark.slow
def test_tc_p08b_the_51_node_shape_renders_and_its_cost_is_recorded():
    """LLR-PERF.1 -- render the shape and RECORD the cost.  No budget asserted.

    The only assertions are that the render produced something and that the shape
    is the declared one.  The elapsed time is reported, never gated: what a
    reasonable budget IS is a design question this batch is forbidden to answer.
    """
    graph = _layered_dag()
    assert len(graph.nodes) == EXPECTED_NODES

    started = time.perf_counter()
    text = LayeredRenderer().render(graph, selected_id="root", w=140, h=45)
    elapsed = time.perf_counter() - started

    assert text.plain.strip(), "the 51-node shape rendered nothing"
    print(
        f"\nLLR-PERF.1 measurement: {EXPECTED_NODES} nodes, {len(graph.edges)} edges, "
        f"LayeredRenderer at 140x45 -> {elapsed:.4f}s  (NO BUDGET ASSERTED -- S-18 "
        "is parked for the feature batch's PDR)"
    )
