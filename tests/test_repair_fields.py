"""Increment 3 — S-02 field integrity, the save refusal (A-2), and A-3.

Layer 0 / A (TC-*) verify the loader and the model; layer B (AT-*) drives the
shipped surface.  Every AT here is one node driving one whole chain (C-18).
"""
from __future__ import annotations

import dataclasses
import pathlib
import sys
from datetime import date, datetime

import pytest
import yaml

from mapper.app import HomeScreen, MapperApp, MapScreen
from mapper.model import Document, Edge, Ficha, Graph, Node
from mapper.store import MapStore, MapStoreError, _text_attributes

SCHEMA = [
    {"key": "D", "label": "documento", "required": True, "kind": "text"},
    {"key": "O", "label": "dueño", "required": True, "kind": "text"},
]


def write_map(tmp_path, nodes: dict, mmd: str = "graph TD\n  root --> a\n"):
    """Write a two-node map plus its sidecar and return a store + id."""
    (tmp_path / "m.mmd").write_text(mmd, encoding="utf-8")
    (tmp_path / "m_nodos.yml").write_text(
        yaml.safe_dump({"schema": SCHEMA, "nodes": nodes}, allow_unicode=True),
        encoding="utf-8",
    )
    return MapStore(tmp_path), "m"


def well_formed() -> dict:
    return {
        "root": {"title": "raíz", "fields": {"D": "doc", "O": "ana"}},
        "a": {"title": "hijo", "fields": {"D": "otro", "O": "beto"}},
    }


# --------------------------------------------------------------------------
# TC-R15 / TC-R16 — the coercion, over a set DERIVED from the model


def test_tc_r15_the_text_attribute_set_is_derived_from_ficha_not_hand_listed():
    """C-31 at the requirement level: the set must come from the model.

    A hand-listed set repairs the members that break today.  This asserts the
    derivation agrees with `Ficha`'s own annotations, so adding a text attribute
    to `Ficha` puts it in scope without anyone remembering to.  The `>= 4` floor
    stops the derivation degrading to an empty tuple, which would make every
    coercion assertion below vacuous while staying green.
    """
    derived = set(_text_attributes())
    expected = {
        f.name
        for f in dataclasses.fields(Ficha)
        if f.type in ("str", str)
    }
    assert derived == expected
    assert len(derived) >= 4, "the derivation collapsed; every coercion check below would go vacuous"
    # `state` is the discriminating negative: no consumer joins it, so a fix
    # shaped to "what breaks today" would leave it out (amendment A-7).
    assert "state" in derived
    assert "fields" not in derived and "attachments" not in derived


@pytest.mark.parametrize(
    "raw,expected",
    [
        (20260826, "20260826"),
        (3.5, "3.5"),
        (True, "True"),
        (False, "False"),
        (None, ""),
        (0, "0"),
    ],
)
def test_tc_r16_a_scalar_field_coerces_deterministically(tmp_path, raw, expected):
    """LLR-R03.1 — scalars become text, and `None` becomes the empty string.

    `0` and `False` are in the set on purpose: they are falsy, so a coercion
    written as `str(v) if v else ""` would pass every other row here and quietly
    erase a real value.
    """
    nodes = well_formed()
    nodes["root"]["fields"]["D"] = raw
    store, map_id = write_map(tmp_path, nodes)
    graph = store.load(map_id)
    value = graph.nodes["root"].ficha.fields["D"]
    assert isinstance(value, str)
    assert value == expected


def test_tc_r16b_a_date_coerces_to_an_iso_string(tmp_path):
    """A YAML `D: 2026-08-26` parses as `datetime.date`, not as text.

    Deterministic means the same bytes on every platform, so the assertion pins
    the ISO form rather than `str(value)`, whose format is a promise nobody made.
    """
    (tmp_path / "m.mmd").write_text("graph TD\n  root --> a\n", encoding="utf-8")
    (tmp_path / "m_nodos.yml").write_text(
        "schema:\n"
        "- {key: D, label: documento, required: true, kind: text}\n"
        "nodes:\n"
        "  root: {title: raíz, fields: {D: 2026-08-26}}\n",
        encoding="utf-8",
    )
    graph = MapStore(tmp_path).load("m")
    assert graph.nodes["root"].ficha.fields["D"] == "2026-08-26"
    assert date(2026, 8, 26).isoformat() == "2026-08-26"
    assert datetime(2026, 8, 26, 7, 5).isoformat() == "2026-08-26T07:05:00"


# --------------------------------------------------------------------------
# TC-R17 / TC-R18 — containers are refused, not coerced


@pytest.mark.parametrize("raw", [{}, {"x": 1}, [], [1, 2]])
def test_tc_r17_a_container_field_becomes_empty_and_is_recorded(tmp_path, raw):
    """LLR-R03.2 — a container is not faithfully representable as ficha text.

    The empty container matters most: `str({})` is `"{}"`, a TRUTHY string, so a
    coercion that accepted containers would leave `coverage()` counting this
    field as documented and the miscount would survive its own fix.
    """
    nodes = well_formed()
    nodes["root"]["fields"]["D"] = raw
    store, map_id = write_map(tmp_path, nodes)
    graph = store.load(map_id)
    assert graph.nodes["root"].ficha.fields["D"] == ""
    assert "campo ilegible: root.D" in graph.load_warnings


def test_tc_r18_a_non_dict_fields_block_does_not_deny_the_map(tmp_path):
    """LLR-R03.5 — a malformed field never denies the whole map.

    `_build_sidecar` cannot emit this; a human editing `_nodos.yml` can.
    """
    nodes = well_formed()
    nodes["root"]["fields"] = ["D", "O"]
    store, map_id = write_map(tmp_path, nodes)
    graph = store.load(map_id)
    assert graph.nodes["root"].ficha.fields == {}
    assert "campo ilegible: root.fields" in graph.load_warnings
    assert set(graph.nodes) == {"root", "a"}


# --------------------------------------------------------------------------
# TC-R19 / TC-R21 — the warning list, and the map still loading


def test_tc_r19_each_malformed_field_gets_one_spanish_warning(tmp_path):
    nodes = well_formed()
    nodes["root"]["fields"]["D"] = {}
    nodes["a"]["fields"]["O"] = [1]
    store, map_id = write_map(tmp_path, nodes)
    graph = store.load(map_id)
    assert sorted(graph.load_warnings) == [
        "campo ilegible: a.O",
        "campo ilegible: root.D",
    ]


def test_tc_r21_a_well_formed_map_records_no_warnings(tmp_path):
    """The discriminating negative for the warning list.

    Without this, a loader that warned about everything would satisfy every
    assertion above — C-53 prices a false alarm as high as a missed one.
    """
    store, map_id = write_map(tmp_path, well_formed())
    graph = store.load(map_id)
    assert graph.load_warnings == []


# --------------------------------------------------------------------------
# AT-R06 / AT-R07 / AT-R07b / AT-R07c — the acceptance chain, through load


def test_at_r06_a_scalar_field_loads_and_every_consumer_survives(tmp_path):
    """AT-R06 — `D: 20260826` was the reported defect, end to end.

    Pre-fix: the load succeeded, `missing_required` raised `AttributeError`,
    `search_hits` raised `TypeError`, and `coverage()` answered `(2, 2)`.
    """
    nodes = well_formed()
    nodes["root"]["fields"]["D"] = 20260826
    store, map_id = write_map(tmp_path, nodes)
    graph = store.load(map_id)

    assert graph.nodes["root"].ficha.fields["D"] == "20260826"
    schema = graph.schema
    assert graph.nodes["root"].ficha.missing_required(schema) == []
    assert graph.search_hits("20260826") == ["root"]
    assert graph.coverage() == (4, 4)


def test_at_r07_a_container_field_loads_and_coverage_calls_it_missing(tmp_path):
    """AT-R07 — the container regression (amendment A-8).

    Pre-fix this node went RED by DENYING the map: `_reindex` binds ficha values
    straight into SQLite, which cannot bind a `dict`.  So the container case is a
    repaired crash and the scalar case is a repaired miscount — different
    defects sharing one fix, and the RED had to be recorded for the right reason.
    """
    nodes = well_formed()
    nodes["root"]["fields"]["D"] = {}
    store, map_id = write_map(tmp_path, nodes)
    graph = store.load(map_id)

    missing = graph.nodes["root"].ficha.missing_required(graph.schema)
    assert [f.key for f in missing] == ["D"]
    assert graph.coverage() == (3, 4)


@pytest.mark.parametrize("raw", [12345, None])
def test_at_r07b_a_non_string_title_loads_and_search_hits_survives(tmp_path, raw):
    """AT-R07b — the out-of-`fields` regression (amendment A-7).

    `search_hits` joins `title`, `meta` and `notes` alongside the field values, so
    a non-string in any of them raises the identical `TypeError`.  `None` is the
    realistic shape: a bare `title:` key is what a hand-edited sidecar produces.
    """
    nodes = well_formed()
    nodes["root"]["title"] = raw
    store, map_id = write_map(tmp_path, nodes)
    graph = store.load(map_id)

    assert isinstance(graph.nodes["root"].ficha.title, str)
    assert graph.search_hits("hijo") == ["a"]


def test_at_r07c_a_non_string_state_also_survives_every_consumer(tmp_path):
    """AT-R07c — the discriminating negative for the derived set.

    `state` is joined by NO consumer, so a fix shaped to "the attributes that
    break today" would leave it a raw `int` and still pass AT-R07b.  This is what
    makes the derivation load-bearing rather than decorative.
    """
    nodes = well_formed()
    nodes["root"]["state"] = 7
    store, map_id = write_map(tmp_path, nodes)
    graph = store.load(map_id)

    assert graph.nodes["root"].ficha.state == "7"
    assert graph.search_hits("raíz") == ["root"]


def test_at_r08_the_operator_is_told_which_node_and_which_field(tmp_path):
    """AT-R08 — the message names both coordinates, not just that something broke."""
    nodes = well_formed()
    nodes["a"]["fields"]["O"] = {"nested": True}
    store, map_id = write_map(tmp_path, nodes)
    graph = store.load(map_id)

    assert graph.load_warnings == ["campo ilegible: a.O"]
    assert "a" in graph.load_warnings[0] and "O" in graph.load_warnings[0]


def test_at_r09_a_well_formed_maps_coverage_is_unchanged(tmp_path):
    """AT-R09 — the discriminating negative for the whole story.

    A fix that counted every field as missing would pass AT-R07 and destroy the
    number the operator plans against.  The expected figure is derived from the
    fixture rather than typed, so changing the fixture cannot silently make this
    assert something else.
    """
    nodes = well_formed()
    store, map_id = write_map(tmp_path, nodes)
    graph = store.load(map_id)

    required = [f["key"] for f in SCHEMA if f["required"]]
    filled = sum(
        1 for n in nodes.values() for k in required if str(n["fields"].get(k, ""))
    )
    assert graph.coverage() == (filled, len(required) * len(nodes))
    assert graph.coverage() == (4, 4)


# --------------------------------------------------------------------------
# The coverage regression US-R03 exists for, asserted on its own


@pytest.mark.parametrize(
    "raw,counts_as_documented",
    [
        ("doc", True),
        (20260826, True),
        (0, True),
        ({}, False),
        ({"a": 1}, False),
        ([], False),
        ([1], False),
        (None, False),
        ("", False),
        ("   ", False),
    ],
)
def test_coverage_never_counts_an_unreadable_field_as_documented(
    tmp_path, raw, counts_as_documented
):
    """HLR-R03's headline clause, isolated so it cannot pass "in parts".

    Both polarities are driven: the readable rows must still COUNT, or a loader
    that zeroed everything would pass the unreadable rows and destroy the figure.
    `0` is the row that separates "readable" from "truthy" — it is falsy and it
    is a real value, so `coverage` counts it while `""` and `"   "` do not.
    """
    nodes = well_formed()
    nodes["root"]["fields"]["D"] = raw
    store, map_id = write_map(tmp_path, nodes)
    graph = store.load(map_id)

    have, req = graph.coverage()
    assert req == 4
    assert have == (4 if counts_as_documented else 3)

    missing = {f.key for f in graph.nodes["root"].ficha.missing_required(graph.schema)}
    assert ("D" in missing) is not counts_as_documented


def test_coverage_is_unreachable_by_a_non_string_after_load(tmp_path):
    """The mechanism, not just the number: nothing non-`str` survives the loader.

    `required_coverage` tests each value for truthiness, so an `int` field would
    be counted as documented while `missing_required` raised on `.strip()`.  This
    asserts the invariant that makes both safe, over every loaded ficha.
    """
    nodes = well_formed()
    nodes["root"]["fields"]["D"] = 20260826
    nodes["root"]["title"] = 99
    nodes["a"]["fields"]["O"] = {}
    store, map_id = write_map(tmp_path, nodes)
    graph = store.load(map_id)

    checked = 0
    for node in graph.nodes.values():
        for attr in _text_attributes():
            assert isinstance(getattr(node.ficha, attr), str)
            checked += 1
        for value in node.ficha.fields.values():
            assert isinstance(value, str)
            checked += 1
    assert checked >= 10, "the sweep found almost nothing; it is not an oracle"


# --------------------------------------------------------------------------
# TC-R20 — the notice reaches the OPERATOR, not just the model
#
# Every assertion above observes `graph.load_warnings`, which is the model.  The
# increment-3 mutation battery found the gap: disabling `_notice_load_warnings`
# entirely reddened NOTHING, because no node drove the shipped surface.  A story
# whose promise is "the operator is told" is not covered by a list on an object.


async def test_tc_r20_the_map_screen_tells_the_operator_about_a_malformed_field(
    tmp_path,
):
    """LLR-R03.4 through the shipped surface, on the screen that opens one map."""
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        nodes = well_formed()
        nodes["root"]["fields"]["D"] = {}
        write_map(app.store.workspace, nodes)

        notices: list[tuple[str, dict]] = []
        app.notify = lambda msg, **kw: notices.append((str(msg), kw))

        app.push_screen(MapScreen("m"))
        await pilot.pause()
        await pilot.pause()

        hits = [(m, kw) for m, kw in notices if "campo ilegible: root.D" in m]
        assert hits, notices
        # ... and the map still opened (LLR-R03.5): this is a notice, not an error.
        assert isinstance(app.screen, MapScreen)
        assert set(app.screen.graph.nodes) == {"root", "a"}
        # The markup defense, armed (review finding F3).  `notify` defaults to
        # `markup=True` and `darkside.plain` deliberately preserves markup, so
        # `markup=False` is the ENTIRE defense at this sink over text that came
        # out of a file.  Capturing kwargs is what makes dropping it redden
        # something instead of nothing.
        assert all(kw.get("markup") is False for _, kw in hits), hits


async def test_tc_r20b_a_well_formed_map_produces_no_such_notice(tmp_path):
    """The discriminating negative: a screen that always warns is not a fix."""
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        write_map(app.store.workspace, well_formed())

        notices: list[str] = []
        app.notify = lambda msg, **kw: notices.append(str(msg))

        app.push_screen(MapScreen("m"))
        await pilot.pause()
        await pilot.pause()

        assert not any("campo ilegible" in n for n in notices), notices
        # The positive control for this absence (C-55): the same harness on the
        # same screen DOES capture the notice in TC-R20, so a zero here is a
        # measurement rather than a probe that cannot fire.


async def test_tc_r20c_the_home_screen_tells_the_operator_too(tmp_path):
    """The sala loads every map on mount, so it is the other surface that owes it."""
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        nodes = well_formed()
        nodes["a"]["fields"]["O"] = [1, 2]
        write_map(app.store.workspace, nodes)
        app.store.record_session("m", "root")

        notices: list[tuple[str, dict]] = []
        app.notify = lambda msg, **kw: notices.append((str(msg), kw))

        app.push_screen(HomeScreen())
        await pilot.pause()

        hits = [(m, kw) for m, kw in notices if "campo ilegible: a.O" in m]
        assert hits, notices
        # The markup defense at the OTHER sink, armed independently (F3).  The two
        # sinks are separate call sites, so one assertion cannot cover both.
        assert all(kw.get("markup") is False for _, kw in hits), hits


# --------------------------------------------------------------------------
# LLR-R01.5 / A-2 — the store refuses to write what it will refuse to read


def cyclic_graph() -> Graph:
    graph = Graph()
    for nid in ("a", "b", "c"):
        graph.add_node(Node(id=nid, ficha=Ficha(title=nid)))
    graph.add_edge(Edge("a", "b"))
    graph.add_edge(Edge("b", "c"))
    graph.add_edge(Edge("c", "a"))
    return graph


def test_tc_r27_save_refuses_a_cyclic_graph_with_the_load_message(tmp_path):
    """LLR-R01.5 — the write side is exactly as strict as the read side."""
    store = MapStore(tmp_path)
    with pytest.raises(MapStoreError) as exc:
        store.save("poison", cyclic_graph())
    assert "el mapa tiene un ciclo" in str(exc.value)
    for nid in ("a", "b", "c"):
        assert nid in str(exc.value)


def test_tc_r28_the_refused_save_leaves_no_file_behind(tmp_path):
    """The discriminating NEGATIVE: assert the file that must not exist.

    The defect A-2 repairs is a persisted unloadable map, so "raised" is not
    enough — a refusal that raises AFTER writing produces the poison pill anyway.
    """
    store = MapStore(tmp_path)
    with pytest.raises(MapStoreError):
        store.save("poison", cyclic_graph())
    assert not (tmp_path / "poison.mmd").exists()
    assert not (tmp_path / "poison_nodos.yml").exists()


def test_at_r15_a_well_formed_graph_still_saves_and_reloads(tmp_path):
    """AT-R15 — the false-refusal control (C-53).

    A refusal that refuses everything passes TC-R27 and breaks the application.
    The fixture is a FORK — one parent, two children — which is the shape a
    naive "have I seen this node before" cycle test flags first, and the shape
    arm M18 of the battery uses.  (A true diamond, where two paths converge on
    one node, is covered by increment 1's `AT-R03b`; `mermaid.parse` has refused
    multiple parents since long before this batch, so it cannot arrive here.)
    """
    graph = Graph()
    for nid in ("root", "l", "r"):
        graph.add_node(Node(id=nid, ficha=Ficha(title=nid)))
    graph.add_edge(Edge("root", "l"))
    graph.add_edge(Edge("root", "r"))
    graph.root_id = "root"

    store = MapStore(tmp_path)
    store.save("ok", graph)
    assert (tmp_path / "ok.mmd").exists()
    assert set(store.load("ok").nodes) == {"root", "l", "r"}


# --------------------------------------------------------------------------
# A-3 — resolve_document is iterative, and agrees with the shipped version


def _shipped_resolve(graph: Graph, name: str, node: Node) -> Document:
    """The pre-repair implementation, verbatim, as the positive control.

    LLR-R02.2's discipline applied to A-3: a rewrite is only correct if it agrees
    with the original everywhere the original terminated.  A rewrite that merely
    stops crashing could be returning anything.
    """
    doc = graph.documents.get(name)
    if doc is None:
        return Document(name=name, source="")
    merged_tags = dict(doc.tags)
    merged_inherited = dict(doc.inherited)
    parent_id = graph.parent_of(node.id)
    if parent_id is not None:
        parent = graph.nodes.get(parent_id)
        if parent is not None:
            parent_doc = _shipped_resolve(graph, name, parent)
            for key, value in parent_doc.tags.items():
                if key not in merged_tags:
                    merged_tags[key] = value
                    merged_inherited[key] = value
    return Document(
        name=doc.name,
        source=doc.source,
        tags=merged_tags,
        inherited=merged_inherited,
        template=doc.template,
        path=doc.path,
        kind=doc.kind,
    )


def _chain(depth: int, tags: dict | None = None) -> Graph:
    graph = Graph()
    graph.add_node(Node(id="n0", ficha=Ficha(title="n0")))
    for i in range(1, depth):
        graph.add_node(Node(id=f"n{i}", ficha=Ficha(title=f"n{i}")))
        graph.add_edge(Edge(f"n{i - 1}", f"n{i}"))
    graph.documents = {"doc": Document(name="doc", source="s", tags=tags or {"k": "v"})}
    return graph


def test_tc_r35_resolve_document_does_not_walk_the_parent_chain(monkeypatch):
    """A-3's GATE. Every other node below is a pin; this is the one that can fail.

    Review finding F1: the first fix replaced the shipped recursion with an
    *iterative* fold that was equally dead, because `documents` is graph-level and
    every level rebuilt the same mapping.  An implementation with the walk deleted
    was indistinguishable from it over every graph, so no equivalence node could
    tell the two apart — and the cycle guard the walk needed had a HANG as its
    only regression mode.

    Counting `parent_of` calls is what makes the walk's ABSENCE assertable.  The
    declared subject is in the expression: reintroduce a chain walk routed
    through `Graph.parent_of` — recursive or iterative — and this reddens instead
    of hanging.

    **Its reach is exactly that and no wider** (re-gate finding `G2`, measured).
    A walk deriving each parent by scanning `self.edges` INLINE never touches
    `parent_of` and leaves this node green, and `TC-R29`'s AST derivation does not
    close the gap either, because an iterative walk is not recursion.  This
    docstring previously claimed "a chain walk of any kind", which was false —
    precisely the overclaim C-40 exists to catch, since a gate is only as broad as
    its own expression.  Widening it means asserting over `resolve_document`'s AST
    that its body contains no loop over `self.edges`; that is filed against
    `TC-R29`'s family rather than bolted on here.
    """
    calls: list[str] = []
    real = Graph.parent_of
    monkeypatch.setattr(
        Graph, "parent_of", lambda self, nid: (calls.append(nid), real(self, nid))[1]
    )

    graph = _chain(400)
    # Positive control: the counter must be able to COUNT.  A monkeypatch that
    # silently failed to bind would read 0 and pass, which is C-55's rider — an
    # absence is admissible only if the probe can produce a non-absence.
    graph.parent_of("n399")
    assert calls == ["n399"], "the call counter is not wired; every count below is vacuous"

    calls.clear()
    doc = graph.resolve_document("doc", graph.nodes["n399"])
    assert doc.tags == {"k": "v"}
    assert calls == [], f"resolve_document walked the parent chain: {len(calls)} steps"


@pytest.mark.parametrize("depth", [1, 2, 3, 7, 40, 120])
def test_tc_r33_resolve_document_agrees_with_the_shipped_implementation(depth):
    """A-3 — equivalence with `master`'s recursion everywhere it terminated.

    A REGRESSION PIN, not a gate (C-40's corollary), and labelled so on purpose:
    the walk it once certified is gone, so no traversal defect can redden it.  It
    earns its place by pinning that removing the walk changed no observable value.

    The comparison count is asserted so a shape that silently produced no
    comparisons cannot report agreement over the empty set.
    """
    graph = _chain(depth, {"k": "v", "j": "w"})
    compared = 0
    for node in graph.nodes.values():
        mine = graph.resolve_document("doc", node)
        theirs = _shipped_resolve(graph, "doc", node)
        assert mine == theirs
        compared += 1
    assert compared == depth
    assert depth >= 1

    # The answer does not depend on the node — the plain statement of what this
    # function does, now that the pretence of per-node inheritance is gone.
    first = graph.resolve_document("doc", graph.nodes["n0"])
    last = graph.resolve_document("doc", graph.nodes[f"n{depth - 1}"])
    assert first == last

    # ... and a caller cannot alias the graph's own mapping through the result.
    first.tags["injected"] = "x"
    assert "injected" not in graph.documents["doc"].tags


def test_tc_r33b_an_unregistered_document_name_agrees_too():
    graph = _chain(3)
    node = graph.nodes["n2"]
    assert graph.resolve_document("nope", node) == _shipped_resolve(graph, "nope", node)


def test_tc_r34_a_cyclic_parent_chain_is_still_answered():
    """A REGRESSION PIN. The recursion looped for ever on a cyclic parent chain.

    With no walk there is nothing to loop, so this cannot fail for the reason it
    was written — only if someone reintroduces a chain walk without a guard.
    `parse` refuses a cyclic edge set now, but `preview_csv` builds a graph that
    never passes through the parser, which is the door A-1 and A-2 exist for.
    """
    graph = Graph()
    for nid in ("a", "b", "c"):
        graph.add_node(Node(id=nid, ficha=Ficha(title=nid)))
    graph.add_edge(Edge("a", "b"))
    graph.add_edge(Edge("b", "c"))
    graph.add_edge(Edge("c", "a"))
    graph.documents = {"doc": Document(name="doc", source="s", tags={"k": "v"})}

    doc = graph.resolve_document("doc", graph.nodes["b"])
    assert doc.tags == {"k": "v"}


@pytest.mark.slow
def test_at_r17_resolve_document_survives_a_depth_5000_chain():
    """A REGRESSION PIN for A-3, and it is labelled so deliberately.

    The recursion limit is left at its default on purpose: raising it moves the
    crash instead of fixing it, which is the plausible-weaker arm HLR-R02 names —
    and the battery MEASURED this node staying GREEN under exactly that arm.  So
    it does not gate the repair; `TC-R35` does.  It is kept because a
    reintroduced recursion still dies here, loudly.
    """
    assert sys.getrecursionlimit() <= 1500
    graph = _chain(5000)
    doc = graph.resolve_document("doc", graph.nodes["n4999"])
    assert doc.tags == {"k": "v"}


def test_tc_r37_an_unparseable_sidecar_is_refused_in_spanish_not_raised_raw(tmp_path):
    """A hostile sidecar scalar is refused as `MapStoreError`, not a bare `ValueError`.

    The branch security pass reported this as `M2` and attributed it to
    `_coerce_field`'s `str(value)`.  **That attribution is wrong, and finding out
    why is the point of this node.**  CPython caps integer PARSING as well as
    integer formatting, and PyYAML's own constructor calls `int(token)` — so a
    sidecar field with more than `sys.get_int_max_str_digits()` digits raises
    inside `yaml.safe_load`, before the coercion ladder runs at all.  A guard in
    `_coerce_field` is unreachable for this input; it was written, measured
    unreachable, and removed.

    **This node asserts refusal, not repair.**  The map is still denied.  One
    unparseable field denying a whole map is `F-M5`'s shape, which is fenced out
    of this batch, and "repairing" it by treating the sidecar as absent would open
    the map with every ficha blank — which `MapStore.save` would then write back
    over the operator's real data.  Refusing loudly is the safer contract for a
    file-backed tool, so what changed is only that the refusal is TYPED, Spanish,
    and names the file.

    RED before the fix: a bare `ValueError` escapes `store.load`, so both the
    `MapStoreError` type and the Spanish message are absent.

    The digits are injected as TEXT, never built as a Python `int`: doing that in
    the fixture hits the same limit inside `yaml.safe_dump` and the test fails
    before it can exercise the loader.
    """
    digits = "9" * (sys.get_int_max_str_digits() + 700)

    (tmp_path / "m.mmd").write_text("graph TD\n  root --> a\n", encoding="utf-8")
    (tmp_path / "m_nodos.yml").write_text(
        yaml.safe_dump({"schema": SCHEMA, "nodes": well_formed()}, allow_unicode=True).replace(
            "D: doc", f"D: {digits}"
        ),
        encoding="utf-8",
    )
    store = MapStore(tmp_path)

    with pytest.raises(MapStoreError) as caught:
        store.load("m")

    message = str(caught.value)
    assert "no se pudo leer la ficha" in message, message
    assert "m_nodos.yml" in message, message
    # The cause is preserved, so the underlying limit is still diagnosable.
    assert isinstance(caught.value.__cause__, ValueError)

    # The discriminating negative: the SAME sidecar with a field one digit under
    # the limit parses and loads normally, so the refusal is attributable to the
    # length and not to the fixture being malformed in some other way.
    ok_digits = "9" * (sys.get_int_max_str_digits() - 1)
    (tmp_path / "m_nodos.yml").write_text(
        yaml.safe_dump({"schema": SCHEMA, "nodes": well_formed()}, allow_unicode=True).replace(
            "D: doc", f"D: {ok_digits}"
        ),
        encoding="utf-8",
    )
    graph = MapStore(tmp_path).load("m")
    assert graph.nodes["root"].ficha.fields["D"] == ok_digits

def test_tc_r38_every_interpolating_notify_passes_markup_false():
    """The markup defense, asserted as a CLASS instead of one sink at a time.

    This exact defect has now been found SIX times by three different reviews —
    increment 1's `F2`, increment 2b's `F3`, the increment-3 re-gate's `G1`, and
    the branch security pass's `M1` (two sites) and `M3` — and each time the
    response was to arm one more sink by hand.  Closing instances does not close
    a class, and the recurrence is the evidence.

    `App.notify` defaults to `markup=True`, and `darkside.plain()` deliberately
    PRESERVES markup, so `markup=False` is the entire defense wherever a message
    interpolates a value.  Measured: a node id `ev[bold red]il[/]x` renders as
    `evilx` under markup parsing — the operator loses the very id they need in
    order to find the fault.

    **The site set is DERIVED by walking the AST of every module** (C-31), never
    hand-listed, so a new sink joins the census the moment it is written.  There
    is deliberately **no exemption list**: an allowlist is itself a hand-listed
    set that rots, and no toast in this application wants markup rendering, so
    the rule can be blanket and the exemption set empty.

    RED arm: drop the keyword at any one site.
    """
    import ast

    offenders: list[str] = []
    scanned = 0
    for path in sorted(pathlib.Path("mapper").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "notify"
                and node.args
            ):
                continue
            first = node.args[0]
            # The rule is SHAPE-FREE on purpose.  The first version of this
            # census required only f-strings, and that shape-based predicate had
            # its own blind spot: `notify(str(exc), ...)` passes a Call, not a
            # JoinedStr, and was skipped — including one live site carrying
            # remote-derived `GitHubError` text with no keyword at all.  A
            # census with a shape-shaped hole does not close a class.
            #
            # The honest rule: anything that is not a compile-time constant can
            # carry injected markup, however it was built — f-string, `%`,
            # `.format()`, concatenation, or a call.
            if isinstance(first, ast.Constant):
                continue  # a literal message cannot carry injected markup
            scanned += 1
            keyword = next((k for k in node.keywords if k.arg == "markup"), None)
            ok = (
                keyword is not None
                and isinstance(keyword.value, ast.Constant)
                and keyword.value.value is False
            )
            if not ok:
                offenders.append(f"{path.as_posix()}:{node.lineno}")

    # The census must be able to FIND something, or the emptiness above is an
    # artifact of a broken walk rather than a property of the tree (C-55's
    # rider): an absence is admissible only if the probe can produce a presence.
    assert scanned >= 15, (
        f"the AST walk found only {scanned} interpolating notify sites; the walk "
        "is broken and its clean result means nothing"
    )
    assert not offenders, (
        f"{len(offenders)} of {scanned} interpolating notify sites do not pass "
        f"markup=False: {offenders}"
    )
