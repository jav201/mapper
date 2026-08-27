"""HLR-STO.1 / LLR-STO.1.1 — the store boundary returns text where text is promised.

The requirement `C-2` and `C-3` were folded into and which did not exist: it was
referenced normatively 24 times across the feature batch's artifacts, with a `shall`,
and had no heading, no threshold and no test anywhere.

THE INPUT SET IS DERIVED, NOT HAND-LISTED (C-31), and the census has been WRONG
TWICE -- each time because a hand exclusion survived inside an otherwise-derived
rule. That history is the argument for the derivation, so it is recorded here:

  * the security lens hand-listed "5 families, 3 raw"; `documents[]` was missing
    entirely and field KEYS were raw while only their values were coerced;
  * the resulting 17-position census still hand-excluded `Document.tags` and
    `Document.inherited`, which are `dict[str, str]` -- text on BOTH sides, and
    round-tripped verbatim -- on the reasoning that they "are dicts by design".
    `Ficha.fields` is the identical shape and was covered from the start. The
    exclusion did not distinguish its members from a covered sibling, which is
    the C-31 defect operating on the census itself (whole-branch QA, HIGH-1).

The census is **21**: 3 structural + 14 scalar text fields + 2 sides x 2
`dict[str, str]` fields. Every one is computed from the dataclasses' own
annotations; a hand-listed domain is an unproven spec claim, not an oracle.

Measured on `master` before the fix: 12 of the 17 then-known positions leaked a
non-`str`, and a container poison raised four UNTYPED exceptions out of `load`.
"""
from __future__ import annotations

import copy
from dataclasses import fields as dc_fields

import pytest
import yaml

from mapper.model import Attachment, Document, Ficha, SchemaField
from mapper.store import MapStore, MapStoreError

MMD = "graph TD\n    A[Alpha] --> B[Beta]\n"

BASE_SIDECAR = {
    "schema": [{"key": "E", "label": "estado", "required": True, "kind": "text"}],
    "documents": [
        {
            "name": "d1",
            "source": "s",
            "tags": {"owner": "ana"},
            "inherited": {"src": "raiz"},
            "template": False,
            "path": "p",
            "kind": "text",
        }
    ],
    "nodes": {
        "A": {
            "title": "Alpha",
            "state": "ok",
            "meta": "m",
            "notes": "n",
            "fields": {"E": "hecho"},
            "attachments": [{"kind": "img", "path": "p.png", "caption": "c"}],
        },
        # `B` MUST carry a full sidecar entry, and this is load-bearing rather
        # than tidiness.  `MMD` declares two nodes; with only `A` described here,
        # `B` loads with a DEFAULT `Ficha` whose every text field is `""` -- so
        # the containment assertion `(position, "") in live` was satisfied
        # GRAPH-WIDE by `B` and could not see `A`'s position being destroyed.
        # Measured: it was inert on the `node.*` arms until `B` was filled in
        # (review G1).  An empty sibling is an emptiness doing work (C-55).
        "B": {
            "title": "Beta",
            "state": "wip",
            "meta": "mb",
            "notes": "nb",
            "fields": {"E": "pendiente"},
            "attachments": [{"kind": "doc", "path": "b.pdf", "caption": "cb"}],
        },
    },
}


def _text_field_names(cls) -> tuple[str, ...]:
    """The `str`-annotated fields of a dataclass -- the derivation, not a list."""
    return tuple(f.name for f in dc_fields(cls) if f.type in ("str", str))


def _str_map_field_names(cls) -> tuple[str, ...]:
    """The `dict[str, str]` fields -- text on BOTH sides, two positions each."""
    return tuple(
        f.name
        for f in dc_fields(cls)
        if f.type in ("dict[str, str]", "dict[str,str]")
    )


def _derived_positions() -> list[str]:
    """Every text position `_build_sidecar` round-trips, derived from the model.

    NOT hand-listed.  Adding a `str` field to any of these dataclasses extends this
    set automatically, which is the property that makes the census an oracle rather
    than a snapshot of what someone remembered.
    """
    out = ["node.id", "fields.key", "fields.value"]
    out += [f"node.{n}" for n in _text_field_names(Ficha)]
    out += [f"attachment.{n}" for n in _text_field_names(Attachment)]
    out += [f"schema.{n}" for n in _text_field_names(SchemaField)]
    out += [f"document.{n}" for n in _text_field_names(Document)]
    # A `dict[str, str]` is TEXT ON BOTH SIDES, and `_build_sidecar` round-trips it
    # verbatim, so it is two positions per field -- exactly like `Ficha.fields`,
    # which was covered from the start as `fields.key`/`fields.value`.  Omitting
    # `Document.tags`/`inherited` made the census 17 where the rule it states makes
    # it 21: the C-31 defect operating on the census itself (whole-branch QA,
    # HIGH-1).  Derived, so a new `dict[str, str]` field cannot be missed either.
    for name in _str_map_field_names(Document):
        out += [f"document.{name}.key", f"document.{name}.value"]
    return out


# A container cannot occupy a MAPPING KEY: `{{'x': 1}: v}` raises
# `TypeError: unhashable type: 'dict'` before any product code runs.  The two key
# positions are therefore excluded from the CONTAINER poison specifically -- not
# skipped for convenience.  The set is asserted below so it cannot quietly grow into
# a way of excusing real gaps (C-55: an emptiness that is doing work gets declared).
#
# THE EXCLUSION IS CONTAINER-SPECIFIC, AND ONLY THAT.  It does not excuse these
# positions from the refusal branch at large: a HASHABLE non-scalar (`bytes`) does
# occupy both of them through ordinary YAML and is refused there, which
# `test_at_p02c` certifies.  The earlier wording granted an exclusion wider than
# its own justification (Inc-1 review, F5).
#
# DERIVED, not hand-listed.  Hand-listing was survivable while there were two;
# adding `Document.tags`/`inherited` made four, and a hand list would have
# silently omitted the new pair -- the same defect as HIGH-1, one level down.
_KEY_POSITIONS = tuple(
    p
    for p in _derived_positions()
    if p == "node.id" or p == "fields.key" or p.startswith("document.") and p.endswith(".key")
)


def _container_poisonable() -> list[str]:
    return [p for p in _derived_positions() if p not in _KEY_POSITIONS]


# The EXACT record each position's refusal must emit -- the whole line, not a
# fragment of it.  A substring check cannot see a corrupted OWNER coordinate while
# the leaf survives: measured, a mutant replacing the owner with `XXXX` reddened 8
# arms, ALL of them in `tests/test_repair_fields.py` and ZERO here -- so this file
# was leaning on another batch's suite for the very property F6 was raised about
# (review C2).  Note `fields.value` is labelled with the field's KEY (`A.E`), not
# the word "value": the naive `position.split(".")[-1]` false-failed a CORRECT
# implementation, which costs exactly as much as passing a wrong one (C-53).
# Asserted TOTAL over the derived census below, so a new position cannot quietly
# skip the check.
_EXPECTED_REFUSAL = {
    "fields.value": "campo ilegible: A.E",
    "node.title": "campo ilegible: A.title",
    "node.state": "campo ilegible: A.state",
    "node.meta": "campo ilegible: A.meta",
    "node.notes": "campo ilegible: A.notes",
    "attachment.kind": "campo ilegible: A.att[0].kind",
    "attachment.path": "campo ilegible: A.att[0].path",
    "attachment.caption": "campo ilegible: A.att[0].caption",
    "schema.key": "campo ilegible: schema[0].key",
    "schema.label": "campo ilegible: schema[0].label",
    "schema.kind": "campo ilegible: schema[0].kind",
    "document.name": "campo ilegible: document[0].name",
    "document.source": "campo ilegible: document[0].source",
    "document.path": "campo ilegible: document[0].path",
    "document.kind": "campo ilegible: document[0].kind",
    "document.tags.key": "campo ilegible: document[0].tags[b'hi']",
    "document.tags.value": "campo ilegible: document[0].tags.t",
    "document.inherited.key": "campo ilegible: document[0].inherited[b'hi']",
    "document.inherited.value": "campo ilegible: document[0].inherited.t",
    # The two key positions, refused with the hashable non-scalar `b"hi"`.
    "node.id": "campo ilegible: node.id[b'hi']",
    "fields.key": "campo ilegible: A.key[b'hi']",
}


def _live_text_values(graph) -> list[tuple[str, object]]:
    """(position, value) for every text position in a loaded graph."""
    out: list[tuple[str, object]] = []
    for f in graph.schema:
        out += [(f"schema.{n}", getattr(f, n)) for n in _text_field_names(SchemaField)]
    for d in graph.documents.values():
        out += [(f"document.{n}", getattr(d, n)) for n in _text_field_names(Document)]
        for name in _str_map_field_names(Document):
            for k, v in getattr(d, name).items():
                out += [(f"document.{name}.key", k), (f"document.{name}.value", v)]
    for nid, node in graph.nodes.items():
        out.append(("node.id", nid))
        out += [(f"node.{n}", getattr(node.ficha, n)) for n in _text_field_names(Ficha)]
        for k, v in node.ficha.fields.items():
            out += [("fields.key", k), ("fields.value", v)]
        for a in node.ficha.attachments:
            out += [
                (f"attachment.{n}", getattr(a, n)) for n in _text_field_names(Attachment)
            ]
    return out


def _poison(sidecar: dict, position: str, value: object) -> dict:
    d = copy.deepcopy(sidecar)
    node = d["nodes"]["A"]
    family, _, attr = position.partition(".")
    if position == "node.id":
        # Re-key A only, so B's described entry survives the poison.
        #
        # THAT IS NECESSARY BUT NOT SUFFICIENT, and saying otherwise here would be
        # the F4 class of defect.  Re-keying removes `A` from the sidecar while
        # `MMD` still declares it, so the parsed `A` loads with a DEFAULT ficha and
        # the empty positions come back: measured, `node.state`/`meta`/`notes` are
        # `""` again under this poison.  Harmless only because `node.id` is in
        # `_KEY_POSITIONS` and never reaches the containment assertion -- if it
        # ever joined `_container_poisonable`, that arm would be born inert
        # (review C1).
        rest = {k: v for k, v in d["nodes"].items() if k != "A"}
        d["nodes"] = {value: node, **rest}
    elif position == "fields.key":
        node["fields"] = {value: "hecho"}
    elif position == "fields.value":
        node["fields"]["E"] = value
    elif family == "node":
        node[attr] = value
    elif family == "attachment":
        node["attachments"][0][attr] = value
    elif family == "schema":
        d["schema"][0][attr] = value
    elif family == "document" and attr.endswith((".key", ".value")):
        # `document.tags.key` / `document.inherited.value` and friends.
        field_name, _, side = attr.partition(".")
        if side == "key":
            d["documents"][0][field_name] = {value: "t"}
        else:
            d["documents"][0][field_name] = {"t": value}
    elif family == "document":
        d["documents"][0][attr] = value
    else:  # pragma: no cover - guards the derivation against an unrouted family
        raise AssertionError(f"no poison route for derived position {position!r}")
    return d


def _write(tmp_path, sidecar: dict) -> MapStore:
    (tmp_path / "m.mmd").write_text(MMD, encoding="utf-8")
    (tmp_path / "m_nodos.yml").write_text(
        yaml.safe_dump(sidecar, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    return MapStore(tmp_path)


# --- TC-P01: the derived set is complete and non-empty -----------------------


def test_tc_p01_the_position_census_is_derived_and_complete():
    """C-31's guard: the input set must be derived AND asserted non-degenerate.

    Without this, a refactor that silently empties `_derived_positions()` would make
    every parametrized test below vanish -- and a suite with zero arms reports green.
    An arm the harness cannot see is an arm it cannot report inert.
    """
    positions = _derived_positions()
    assert len(positions) == len(set(positions)), "derived positions must be unique"
    # 3 structural (node id, field key, field value) + the dataclasses' own str fields.
    expected = (
        3
        + sum(len(_text_field_names(c)) for c in (Ficha, Attachment, SchemaField, Document))
        + 2 * len(_str_map_field_names(Document))
    )
    assert len(positions) == expected
    assert len(positions) >= 21, (
        "the census is 21: 17 scalar text positions plus the two sides of each of "
        "Document's two `dict[str, str]` fields (whole-branch QA, HIGH-1)"
    )
    for family in ("document.", "attachment.", "schema.", "node."):
        assert any(p.startswith(family) for p in positions), (
            f"family {family!r} vanished from the derived set -- the hand-listed "
            "census that omitted `documents[]` is exactly this failure"
        )


def test_tc_p01c_the_container_exclusion_is_justified_not_merely_declared():
    """The excluded positions must be excluded for a REASON that still holds.

    `_KEY_POSITIONS` removes two arms from thresholds 2 and 3.  An exclusion list is
    the classic place a real gap hides, so this asserts the justification directly:
    a container genuinely cannot occupy those positions, and every OTHER derived
    position genuinely can.  If a future position joins the exclusion without being
    unhashable-bound, this reddens.
    """
    for position in _KEY_POSITIONS:
        with pytest.raises(TypeError, match="unhashable"):
            _poison(BASE_SIDECAR, position, {"x": 1})
    for position in _container_poisonable():
        # Must NOT raise: these arms are genuinely exercisable, so their inclusion
        # in thresholds 2 and 3 is real coverage rather than a parametrize that
        # silently resolves to nothing.
        _poison(BASE_SIDECAR, position, {"x": 1})
    assert set(_KEY_POSITIONS) | set(_container_poisonable()) == set(
        _derived_positions()
    ), "the two sets must partition the derived census -- no position may vanish"
    # The content-check map must be TOTAL over the census: a position with no
    # fragment would raise `KeyError` rather than skip, but asserting it here says
    # so at the point the census is defined instead of at the point it breaks.
    assert set(_EXPECTED_REFUSAL) == set(_derived_positions()), (
        "every derived position needs a declared exact refusal record"
    )


def test_tc_p01b_positive_control_a_clean_map_is_all_text(tmp_path):
    """The probe must be able to report a non-absence, or its zeros mean nothing."""
    store = _write(tmp_path, BASE_SIDECAR)
    graph = store.load("m")
    live = _live_text_values(graph)
    assert live, "positive control observed no positions at all"
    assert [p for p, v in live if not isinstance(v, str)] == []


# --- TC-P02 / AT-P01: coercible scalars are coerced at the boundary ----------


@pytest.mark.parametrize("position", _derived_positions())
def test_at_p01_every_derived_position_coerces_a_scalar(tmp_path, position):
    """AT-P01 -- poisoning ANY derived position still yields all-`str` after load.

    Pre-fix this reddened on 12 of 17 arms.  The verdict is per resolved arm: an
    inert arm hides behind a sibling that failed, and `passed` sits unread.
    """
    store = _write(tmp_path, _poison(BASE_SIDECAR, position, 12345))
    graph = store.load("m")
    offenders = sorted({p for p, v in _live_text_values(graph) if not isinstance(v, str)})
    assert offenders == [], (
        f"poisoning {position} left non-str at {offenders} -- the store boundary "
        "promises text and delivered another type"
    )


# --- TC-P03 / AT-P02: containers are refused and recorded, never coerced -----


@pytest.mark.parametrize("position", _container_poisonable())
def test_at_p02_a_container_is_refused_and_recorded_never_coerced(tmp_path, position):
    """AT-P02 -- a container must NOT become text.

    `str({})` is `"{}"`, a truthy string, so a coercing implementation would keep
    counting the malformed field as documented and the miscount would survive its
    own fix.  This is `M-STO-b`, and it is why threshold 2 exists separately.
    """
    store = _write(tmp_path, _poison(BASE_SIDECAR, position, {"x": 1}))
    graph = store.load("m")
    live = _live_text_values(graph)
    offenders = sorted({p for p, v in live if not isinstance(v, str)})
    assert offenders == [], f"container at {position} left non-str at {offenders}"
    assert not any(
        v in ("{'x': 1}", '{"x": 1}') for _, v in live
    ), f"container at {position} was COERCED to its repr instead of refused"

    # THE CONTAINMENT HALF.  `offenders == []` is satisfied VACUOUSLY by an
    # implementation that DESTROYS the offending entity -- a dropped position
    # offends nothing.  Threshold 2 requires the position to survive as `""`, so
    # `coverage()` keeps counting it as undocumented and the next save does not
    # delete it from disk.  Measured: without this assertion a
    # drop-instead-of-refuse mutant passed all 139 store-facing arms and all 57
    # arms of this file (Inc-1 review, F1).
    assert (position, "") in live, (
        f"{position} was DROPPED, not left empty -- a refused position must survive "
        f"as '' ; observed {sorted({p for p, _ in live})}"
    )

    # Content, not truthiness: a record naming the wrong field is barely better
    # than no record, and there was a live mislabel the weak form could not see
    # (Inc-1 review, F6).
    assert _EXPECTED_REFUSAL[position] in graph.load_warnings, (
        f"container at {position} recorded {graph.load_warnings!r}; expected the "
        f"exact record {_EXPECTED_REFUSAL[position]!r}"
    )


# --- TC-P04 / AT-P03: rejection is typed --------------------------------------


@pytest.mark.parametrize("position", _container_poisonable())
def test_at_p03_rejection_is_always_a_typed_mapstore_error(tmp_path, position):
    """AT-P03 -- `load` raises only `MapStoreError` (S-11) on the container poisons.

    Measured pre-fix: a container poison raised `sqlite3.ProgrammingError` x3 and
    `TypeError` x1 out of `load` itself, so `except MapStoreError` callers -- which
    is every caller -- did not catch them.

    THIS IS A REGRESSION PIN, NOT A GATE, and it is labelled so deliberately (C-40's
    corollary).  Once the coercion ladder above covers every derived position, NO
    container poison reaches the typed-refusal net any more: these arms pass whether
    the net exists or not, so they cannot certify it.  Measured -- removing the net
    entirely reddens ZERO of these arms.  The net is gated by the two tests below,
    which construct the cases the poison census structurally cannot contain (C-55
    limb 2: a guard that is a no-op on today's data is untested however green).
    """
    store = _write(tmp_path, _poison(BASE_SIDECAR, position, {"x": 1}))
    try:
        store.load("m")
    except MapStoreError:
        pass
    except Exception as exc:  # noqa: BLE001 - the point of the test
        pytest.fail(
            f"{position} leaked {type(exc).__name__} out of load; callers catch "
            f"MapStoreError only. {exc}"
        )


# --- TC-P04b / AT-P03: the typed-refusal net is gated by SHAPE poisons ---------
#
# The position census poisons VALUES, so it can never produce the shape errors the
# net exists for.  These shapes are established as net-reaching independently of the
# net itself: each one's `__cause__` is asserted to be a non-`MapStoreError`, which
# is only true if an untyped exception was raised and converted.  An arm whose cause
# is absent would be passing through some earlier typed guard instead, and would be
# certifying nothing.

_MALFORMED_SHAPES = {
    "nodes-is-a-list": lambda d: d.__setitem__("nodes", [1, 2]),
    "node-is-a-scalar": lambda d: d["nodes"].__setitem__("A", 7),
    "schema-is-a-mapping": lambda d: d.__setitem__("schema", {"k": "v"}),
    "schema-item-is-a-scalar": lambda d: d.__setitem__("schema", [7]),
    "document-item-is-a-scalar": lambda d: d.__setitem__("documents", [7]),
}


# The sibling family whose scalar item is REFUSED-AND-RECORDED rather than raised:
# a malformed attachment entry must not deny the whole map, but it must not vanish
# silently either.  Its absence from the set above was the corroborating half of
# the F1 finding -- every other family's "item is a scalar" case was present, and
# the one family that swallowed its scalar was the one missing.
# Each case declares the EXACT records it must produce, in full.  A substring or
# truthiness check cannot see a record whose payload is corrupted while its noun
# survives, which is the weakness F6 fixed for the refusal records and G2 fixes
# here: the index and the coordinates are the part a mutant moves.
_MALFORMED_ITEM_LISTS = {
    "attachment-item-is-a-scalar": (
        lambda d: d["nodes"]["A"].__setitem__("attachments", [{"kind": "img"}, 7]),
        ["campo ilegible: A.attachments[1]"],
        True,  # a well-formed sibling exists and must survive
    ),
    "attachment-item-is-a-string": (
        lambda d: d["nodes"]["A"].__setitem__(
            "attachments", [{"kind": "img"}, "junk", None]
        ),
        # TWO malformed entries at DISTINCT indices: without G4's index these two
        # records would be byte-identical and this arm could not tell them apart.
        ["campo ilegible: A.attachments[1]", "campo ilegible: A.attachments[2]"],
        True,
    ),
    "attachments-is-a-scalar": (
        lambda d: d["nodes"]["A"].__setitem__("attachments", "junk"),
        ["campo ilegible: A.attachments"],
        # The WHOLE list is malformed, so there is no well-formed sibling to
        # survive.  Asserting one here would demand behaviour the input makes
        # impossible -- a predicate that false-fails correct code (C-53).
        False,
    ),
}


@pytest.mark.parametrize("shape", sorted(_MALFORMED_ITEM_LISTS))
def test_at_p02b_a_malformed_list_item_is_recorded_not_swallowed(tmp_path, shape):
    """AT-P02 -- refusing a malformed entry must leave a record (Inc-1 review, F1).

    The load must SUCCEED (a malformed attachment never denies the map) and the
    refusal must be visible.  Pre-fix the entry was filtered out by a bare
    `isinstance(a, dict)` guard with no record at all, so the operator lost data on
    the next save with nothing anywhere saying so.
    """
    mutate, expected, sibling_survives = _MALFORMED_ITEM_LISTS[shape]
    sidecar = copy.deepcopy(BASE_SIDECAR)
    mutate(sidecar)
    graph = _write(tmp_path, sidecar).load("m")
    # The expectation set must be non-empty, or the loop below certifies nothing.
    assert expected, f"{shape} declared no expected record"
    for record in expected:
        assert record in graph.load_warnings, (
            f"{shape}: expected the exact record {record!r}; got "
            f"{graph.load_warnings!r}"
        )
    if sibling_survives:
        # Refusing the malformed entry must not take the well-formed one with it,
        # which is the whole reason this family warns instead of raising.
        assert graph.nodes["A"].ficha.attachments, (
            f"{shape}: refusing the malformed entry destroyed its well-formed sibling"
        )


# --- The two positions the container census cannot reach ----------------------
#
# `_KEY_POSITIONS` is excluded from the container thresholds because a container
# is unhashable.  That argument is CONTAINER-SPECIFIC, and the exclusion it was
# granted covered the whole refusal branch -- wider than its justification
# (Inc-1 review, F5).  A hashable non-scalar reaches both positions through
# ordinary YAML and is refused there, so the refusal branch at those two
# positions is certified here rather than excused.

_HASHABLE_REFUSABLE = b"hi"


@pytest.mark.parametrize("position", _KEY_POSITIONS)
def test_at_p02c_a_key_position_refuses_a_hashable_non_scalar(tmp_path, position):
    """A `bytes` key is hashable, so it OCCUPIES the position and is then refused."""
    sidecar = _poison(BASE_SIDECAR, position, _HASHABLE_REFUSABLE)
    graph = _write(tmp_path, sidecar).load("m")
    assert [p for p, v in _live_text_values(graph) if not isinstance(v, str)] == []
    assert _EXPECTED_REFUSAL[position] in graph.load_warnings, (
        f"{position} refused a bytes key but recorded {graph.load_warnings!r}; "
        f"expected the exact record {_EXPECTED_REFUSAL[position]!r}"
    )


# Each collision case declares its EXACT record.  `any("duplicado" in w)` was too
# weak: a mutant could swap the two nouns AND corrupt both payloads and still pass,
# because "duplicado" survives either way (review G2).  The noun, the coordinates
# and the raw origin are all asserted, so a mutant has nothing left to move.
_COLLISIONS = {
    "field-keys-coerce-together": (
        lambda d: d["nodes"]["A"].__setitem__("fields", {1: "from-int", "1": "from-str"}),
        "campo duplicado: A.'1' <- '1'",
    ),
    # BOTH ids must be present: `1` alone coerces to `"1"`, which collides with
    # nothing in a fixture whose nodes are `A` and `B`.  My first version asserted
    # a record the input could not produce.
    "node-ids-coerce-together": (
        lambda d: d["nodes"].update({1: {"title": "g-int"}, "1": {"title": "g-str"}}),
        "nodo duplicado: '1' <- '1'",
    ),
    "node-ids-both-refused-collapse-onto-empty": (
        lambda d: d["nodes"].update({b"h1": {"title": "g1"}, b"h2": {"title": "g2"}}),
        "nodo duplicado: '' <- b'h2'",
    ),
    # G3: the ungated sibling of the two above.  Note this fires WITHOUT any
    # coercion, which is declared as a deliberate superset in `_graph_from_sidecar`.
    "document-names-coerce-together": (
        # Same correction as the node-id case: the fixture's only document is
        # `d1`, so a lone `1` collides with nothing.  The int is appended SECOND
        # so the record's raw origin shows the coercion that caused the collision.
        lambda d: d["documents"].extend(
            [{"name": "1", "source": "s2"}, {"name": 1, "source": "s3"}]
        ),
        "documento duplicado: '1' <- 1",
    ),
    "document-names-are-plainly-identical": (
        lambda d: d["documents"].append({"name": "d1", "source": "s2"}),
        "documento duplicado: 'd1' <- 'd1'",
    ),
}


@pytest.mark.parametrize("case", sorted(_COLLISIONS))
def test_at_p02d_a_collision_is_recorded_with_its_coordinates(tmp_path, case):
    """A collision destroys operator data on the next save, so it must be recorded.

    Two distinct keys in YAML can be one after coercion; keeping the last silently
    deletes the first from disk (F3 for fields, F4 for node ids, G3 for documents).
    """
    mutate, expected = _COLLISIONS[case]
    sidecar = copy.deepcopy(BASE_SIDECAR)
    mutate(sidecar)
    graph = _write(tmp_path, sidecar).load("m")
    assert expected in graph.load_warnings, (
        f"{case}: expected the exact record {expected!r}; got {graph.load_warnings!r}"
    )


def test_at_p02f_a_well_formed_map_records_no_collision(tmp_path):
    """The negative control: the collision records must not fire on a clean map.

    Without this, a mutant that appends a collision record UNCONDITIONALLY passes
    every arm above -- they only assert the record is present.
    """
    graph = _write(tmp_path, BASE_SIDECAR).load("m")
    assert [w for w in graph.load_warnings if "duplicado" in w] == [], (
        f"a clean map reported a collision: {graph.load_warnings!r}"
    )


# --- Poisoning by OMISSION: a shape the value census cannot reach --------------


@pytest.mark.parametrize(
    "family,key,expected",
    [("schema", "kind", "text"), ("documents", "kind", "text")],
)
def test_at_p01b_an_absent_field_keeps_the_dataclass_default(
    tmp_path, family, key, expected
):
    """The census poisons VALUES, so absence is a shape it structurally cannot reach.

    `_coerce_text_fields` hard-coded `""` for a missing key, which silently rewrote
    a `kind`-less legacy sidecar's `"text"` to `""` -- and `_build_sidecar` writes
    it straight back to disk on the next save (Inc-1 review, F2).
    """
    sidecar = copy.deepcopy(BASE_SIDECAR)
    sidecar[family][0].pop(key)
    graph = _write(tmp_path, sidecar).load("m")
    observed = (
        graph.schema[0].kind if family == "schema"
        else next(iter(graph.documents.values())).kind
    )
    assert observed == expected, (
        f"{family}.{key} was absent and became {observed!r}; the dataclass default "
        f"is {expected!r} and this diff must not re-default it"
    )


@pytest.mark.parametrize("shape", sorted(_MALFORMED_SHAPES))
def test_at_p03b_a_malformed_shape_is_refused_as_a_typed_error(tmp_path, shape):
    """AT-P03 -- an untyped escape from the sidecar walk is converted, not leaked.

    Every caller in the product catches `MapStoreError`; anything else escapes to
    the top level and kills the screen.  `US-N13`'s «sala» loads every map in the
    workspace on mount, so one malformed sidecar anywhere takes the whole mount
    down -- which is the ordering argument this batch exists for.
    """
    sidecar = copy.deepcopy(BASE_SIDECAR)
    _MALFORMED_SHAPES[shape](sidecar)
    store = _write(tmp_path, sidecar)
    with pytest.raises(MapStoreError) as caught:
        store.load("m")
    cause = caught.value.__cause__
    assert cause is not None and not isinstance(cause, MapStoreError), (
        f"{shape} did not go through the typed-refusal net (cause={cause!r}); this "
        "arm would pass with the net removed and so cannot certify it"
    )


def test_at_p03c_a_top_level_non_mapping_sidecar_is_refused(tmp_path):
    """A sidecar that is a list reached `.get` and raised a bare `AttributeError`."""
    (tmp_path / "m.mmd").write_text(MMD, encoding="utf-8")
    (tmp_path / "m_nodos.yml").write_text("- 1\n- 2\n", encoding="utf-8")
    with pytest.raises(MapStoreError):
        MapStore(tmp_path).load("m")


def test_at_p03d_an_indexing_failure_is_refused_as_a_typed_error(tmp_path, monkeypatch):
    """AT-P03 -- the net around `_reindex` converts an arbitrary escape.

    SYNTHETIC BY NECESSITY, and that is the discharge rather than a shortcut (C-55).
    Pre-fix, `_reindex` raised `sqlite3.ProgrammingError` when handed a non-`str`;
    with the ladder in place no constructible sidecar reaches it in a failing state
    any more.  The emptiness is doing work, so the case the tree cannot contain is
    injected: without this arm, deleting that net reddens nothing at all.
    """
    store = _write(tmp_path, BASE_SIDECAR)

    def boom(*_args, **_kwargs):
        raise RuntimeError("indice corrupto")

    monkeypatch.setattr(MapStore, "_reindex", boom)
    with pytest.raises(MapStoreError):
        store.load("m")


# --- AT-P03 continued: the escapes the whole-branch security review measured ---
#
# Threshold 3 said `load` raises only `MapStoreError`.  These three classes still
# escaped it while the suite was fully green, which is the point: the arms below
# exist because the requirement's own criterion was unmet and nothing noticed
# (security review F1/F3).  Each is driven by BYTES, because the defect is in
# decoding and a `str` fixture cannot reach it.

_BAD_BYTES = {
    # `read_text` sat outside every net: invalid UTF-8 in either file raised a
    # bare `UnicodeDecodeError` straight out of `load`.
    "sidecar-invalid-utf8": (MMD.encode("utf-8"), b"nodes:\n  a:\n    title: \xff\xfe\n"),
    "mmd-invalid-utf8": (b"graph TD\n    A[\xff\xfe] --> B[B]\n", b"{}"),
    # PyYAML's scanner recurses per nesting level, so a ~4 KB sidecar exhausts the
    # stack INSIDE `safe_load`, where the old net caught only YAMLError/ValueError.
    "parser-recursion": (
        MMD.encode("utf-8"),
        b"nodes:\n  a:\n    fields:\n      k: " + b"[" * 2000 + b"]" * 2000 + b"\n",
    ),
}


@pytest.mark.parametrize("case", sorted(_BAD_BYTES))
def test_at_p03e_a_decoding_or_recursion_failure_is_refused_as_a_typed_error(
    tmp_path, case
):
    """AT-P03 -- threshold 3 covers the READS and the PARSER, not just the walk."""
    mmd_bytes, yml_bytes = _BAD_BYTES[case]
    (tmp_path / "m.mmd").write_bytes(mmd_bytes)
    (tmp_path / "m_nodos.yml").write_bytes(yml_bytes)
    with pytest.raises(MapStoreError) as caught:
        MapStore(tmp_path).load("m")
    # The operator-facing text must never carry a filesystem path: an `OSError`
    # or `sqlite3` string routinely embeds one, username included (F3).
    assert str(tmp_path) not in str(caught.value), (
        f"{case} leaked a filesystem path into operator-facing text: {caught.value}"
    )


def test_at_p03f_the_top_level_type_guard_is_distinguishable_from_the_net(tmp_path):
    """The `isinstance(sidecar, dict)` refusal is a control, and needs its own arm.

    Deleting that guard entirely leaves every other arm GREEN, because the broad
    `except Exception` net catches the resulting `AttributeError` and re-raises the
    same error type -- a broad net making a specific control untestable (security
    review F7).  The guard raises WITHOUT `from`, and every net arm raises
    `from exc`, so `__cause__` distinguishes them exactly.
    """
    (tmp_path / "m.mmd").write_text(MMD, encoding="utf-8")
    (tmp_path / "m_nodos.yml").write_text("- 1\n- 2\n", encoding="utf-8")
    with pytest.raises(MapStoreError) as caught:
        MapStore(tmp_path).load("m")
    assert caught.value.__cause__ is None, (
        "the top-level type guard was removed: this refusal came through the "
        f"generic net instead (__cause__={caught.value.__cause__!r})"
    )
