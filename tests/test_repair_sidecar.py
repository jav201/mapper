"""Inc-REPAIR S-E — the sidecar's shipped defects, and the coercion sink beside them.

`AT-049` (`B-29`, `LLR-REPAIR.1`) · `AT-050` (`B-30`, `LLR-REPAIR.2`) ·
`B-48` (the attachments phantom) · `LLR-N13.1.7` (alias amplification) ·
the `screens/coverage.py` coercion sink.

**`AT-049` AND `AT-050` HAD NO NODES ON DISK.** They were ratified in
`01-requirements.md` §3.9 and never written — the `AT-005`/`AT-006` shape this
batch already carries, found at the pre-gate before any fix. This module is their
home.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from mapper.store import MapStore, MapStoreError

MMD = "graph TD\n    raiz[Raiz]\n    raiz --> hijo[Hijo]\n"


def _write(tmp_path, sidecar: str):
    (tmp_path / "m.mmd").write_text(MMD, encoding="utf-8")
    (tmp_path / "m_nodos.yml").write_text(sidecar, encoding="utf-8")
    return MapStore(tmp_path)


def amplified(levels: int, fanout: int = 10) -> str:
    """A sidecar whose two `documents` share an alias-amplified `name`.

    TWO documents, because the defect lives in the DUPLICATE branch -- a single
    amplified name never reaches the line that interpolates it.
    """
    lines = ["_anchors:", "  a: &l0 x"]
    for i in range(1, levels + 1):
        refs = ", ".join([f"*l{i-1}"] * fanout)
        lines.append(f"  n{i}: &l{i} [{refs}]")
    deep = f"*l{levels}"
    return "\n".join(lines) + "\n" + "\n".join([
        "schema: []",
        "documents:",
        f"  - name: {deep}",
        "    path: a.pdf",
        f"  - name: {deep}",
        "    path: b.pdf",
        "nodes:",
        "  raiz:",
        "    title: benigno",
        "",
    ])


# ---------------------------------------------------------------------------
# AT-049 / LLR-REPAIR.1 / B-29


def test_at049_a_phantom_sidecar_id_records_a_load_warning(tmp_path):
    """A sidecar id the `.mmd` never defines must be NAMED in a load warning.

    `LLR-REPAIR.1`'s threshold is quantified over EVERY phantom id, not over the
    fixture's one, so two are planted and both must be named.

    Measured pre-fix: `load_warnings == []`. Nothing named either. That silence
    matters beyond tidiness -- `LLR-N13.1.5`'s containment arm, which `AT-025b`
    drives and `HLR-N13.3` leans on, cannot see a damaged sidecar the store does
    not report.
    """
    store = _write(tmp_path, "\n".join([
        "schema: []",
        "nodes:",
        "  raiz:",
        "    title: Raiz",
        "  fantasma:",
        "    title: No existe en el mmd",
        "  segundo_fantasma:",
        "    title: Tampoco existe",
        "",
    ]))
    graph = store.load("m")

    # SET EQUALITY, not per-phantom membership. `LLR-REPAIR.1`'s restated
    # threshold says "the set of named ids shall equal the set of phantoms --
    # set equality, not a count", and the first version of this arm used `any()`
    # per phantom, which cannot see an implementation that names EVERY id.
    named = {
        w.split("'")[1] for w in graph.load_warnings
        if w.startswith("nodo fantasma:")
    }
    assert named == {"fantasma", "segundo_fantasma"}, (
        f"the named phantoms are {named}; the sidecar's phantoms are "
        f"{{'fantasma', 'segundo_fantasma'}}. Warnings: {graph.load_warnings}"
    )
    # AND THE WARNING MUST NOT CHANGE WHAT THE MAP IS. `LLR-REPAIR.1` says the
    # store shall warn "and shall not change the meaning of the coverage values
    # it returns", so the phantom is REPORTED, not REMOVED -- dropping it would
    # move `coverage()`'s denominator, which is the one thing the requirement
    # forbids.
    #
    # The first version of this arm asserted the phantom was ABSENT. That was my
    # over-specification, not the requirement's: it contradicted the clause it
    # was written to enforce, and the fix made it fail. Reported-not-removed is
    # the whole point -- a warning that silently changed the arithmetic would be
    # a second defect wearing the first one's fix.
    assert "fantasma" in graph.nodes
    assert set(graph.nodes) == {"raiz", "hijo", "fantasma", "segundo_fantasma"}


def test_at049_a_clean_sidecar_records_no_phantom(tmp_path):
    """`AT-049`'s NEGATIVE arm, mandated verbatim by the boundary catalog.

    §3.9 requires it: "drives the same workspace with the phantom removed and
    asserts NO warning and a healthy card, so the positive arm is not passing on
    a constant." It was not written, and the code review fired what that costs:
    moving the `append` out of its `if nid not in graph.nodes:` guard -- one
    indentation level, and the shape an implementer reaches for -- makes the
    store warn for EVERY sidecar id, so every healthy map raises a toast naming
    each node. All seven arms stayed green.

    A positive arm alone cannot tell "names the phantoms" from "names
    everything".
    """
    store = _write(tmp_path, "\n".join([
        "schema: []",
        "nodes:",
        "  raiz:",
        "    title: Raiz",
        "  hijo:",
        "    title: Hijo",
        "",
    ]))
    graph = store.load("m")

    assert [w for w in graph.load_warnings if "fantasma" in w] == [], (
        "a sidecar whose ids all exist in the .mmd raised a phantom warning: "
        f"{graph.load_warnings}"
    )
    assert set(graph.nodes) == {"raiz", "hijo"}


# ---------------------------------------------------------------------------
# AT-050 / LLR-REPAIR.2 / B-30


def test_at050_a_not_found_message_names_the_map_not_the_filesystem(tmp_path):
    """The message names the MAP. It must not disclose the filesystem.

    Measured pre-fix: `Map not found: <absolute path>\\no_such_map.mmd` -- the
    full path including the operator's home directory. That string reaches the
    `load_or_notice` toast, so it is operator-visible and screenshot-visible.
    """
    store = MapStore(tmp_path)
    with pytest.raises(MapStoreError) as caught:
        store.load("no_such_map")
    message = str(caught.value)

    assert "no_such_map" in message, (
        f"the message must name the map the operator asked for: {message!r}"
    )
    assert str(tmp_path) not in message, (
        f"the message discloses the workspace path: {message!r}"
    )
    # `LLR-REPAIR.2`'s second numeric clause, which was not asserted: the id
    # appears EXACTLY ONCE. A message that named it twice, or that appended a
    # workspace component, would pass a mere containment check.
    assert message.count("no_such_map") == 1, (
        f"the map id appears {message.count('no_such_map')} times: {message!r}"
    )
    for marker in ("\\", "/", ".mmd"):
        assert marker not in message, (
            f"the message carries a filesystem detail {marker!r}: {message!r}"
        )


def test_at050_the_message_discloses_no_workspace_component(tmp_path):
    """`AT-050`'s boundary arm: a SENTINEL, not a separator.

    The arm above asserts no `/` or `\` appears, and that proxy does not
    generalise -- a map id the operator typed as `sub/dir/mapa` puts a separator
    in the message legitimately, and the arm would call the store guilty for
    echoing what it was asked for. The requirement's oracle is whether a
    WORKSPACE COMPONENT leaks, so the workspace is given a component that cannot
    appear by coincidence.
    """
    marker = "zzsentinelzz"
    workspace = tmp_path / marker
    workspace.mkdir()
    store = MapStore(workspace)

    with pytest.raises(MapStoreError) as caught:
        store.load("no_such_map")
    message = str(caught.value)

    assert marker not in message, (
        f"the message discloses a workspace path component: {message!r}"
    )
    assert "no_such_map" in message


# ---------------------------------------------------------------------------
# B-48 — the attachments phantom


def test_b48_a_mapping_without_attachment_keys_is_refused_not_invented(tmp_path):
    """`attachments` validates TYPE but not CONTENT.

    A scalar entry is correctly refused with a warning. A MAPPING carrying none
    of the attachment keys is accepted SILENTLY as an `Attachment` with empty
    kind, path and caption -- so nothing is lost and a phantom is INVENTED.

    `store.py`'s own comment records that malformed attachments used to be
    discarded silently and that this was fixed. The fix covered scalars and not
    mappings, which is a declaration outrunning the code.

    THE REFUSAL IS KEY-BASED, AND THIS ARM'S FIRST CLAIM WAS CONTENT-BASED.
    A hand-written `kind: null / path: null / caption: null` still yields an
    Attachment with three empty strings -- the reviewer fired it -- and that is
    CORRECT: those keys are an operator's deliberately-empty attachment, and
    refusing on emptiness would destroy it on the next save. What is refused is
    a mapping sharing NONE of the attachment keys. The arm's fixture happens to
    use an unknown key, so the original wording ("no empty attachment survives")
    was true of the fixture and false of the rule.
    """
    store = _write(tmp_path, "\n".join([
        "schema: []",
        "nodes:",
        "  raiz:",
        "    title: Raiz",
        "    attachments:",
        "      - title: soy-un-nodo-no-un-adjunto",
        "      - 42",
        "",
    ]))
    graph = store.load("m")
    attachments = graph.nodes["raiz"].ficha.attachments

    # The scalar is already refused -- the control that shows the arm is not
    # asserting a blanket "nothing is ever accepted".
    assert any("attachments[1]" in w for w in graph.load_warnings), (
        "the scalar entry should already be refused with a coordinate; if this "
        f"fails the fixture no longer exercises the asymmetry. {graph.load_warnings}"
    )
    assert attachments == [], (
        f"{len(attachments)} attachment(s) were INVENTED from a mapping sharing "
        "none of the attachment keys. Neither entry in this fixture names kind, "
        f"path or caption. Warnings: {graph.load_warnings}"
    )
    assert any("adjunto sin campos" in w for w in graph.load_warnings), (
        f"the mapping was dropped without a record: {graph.load_warnings}"
    )


# ---------------------------------------------------------------------------
# LLR-N13.1.7 — alias amplification, by STRUCTURE not by clock


def test_llr_n13_1_7_refusal_warnings_carry_coordinates_not_values(tmp_path):
    """THE MESSAGE REPORTING THE REFUSAL MUST NOT PERFORM THE MATERIALISATION.

    The per-key coercion DOES refuse an alias-amplified value -- `campo ilegible:
    document[0].name` is emitted and the name is coerced to `''`. The duplicate
    branch then interpolates the RAW, UNCOERCED value with `!r`, which
    materialises the very structure the refusal prevented.

    THE ORACLE IS THE MESSAGE'S SIZE, NOT THE CLOCK. That is what makes this arm
    deterministic and cheap: warning length grows 10x per amplification level
    while wall time barely moves at shallow depths. Measured on the shipped
    tree -- benign 31 chars; 5 levels 522,311 chars in 0.025 s. Five levels is
    driven here precisely because it is RED by four orders of magnitude while
    costing 25 ms, so the default lane carries no wall-clock assert (`FLAKE-1`
    is what that discipline is for).
    """
    graph = _write(tmp_path, amplified(levels=5)).load("m")
    total = sum(len(w) for w in graph.load_warnings)

    # POSITIVE CONTROL FIRST. This arm is a pure UPPER bound, so deleting the
    # diagnostic entirely is a green way to pass it -- fired and confirmed by
    # the code review. The record must exist before its size is judged.
    assert any(w.startswith("documento duplicado:") for w in graph.load_warnings), (
        f"the duplicate record is missing entirely: {graph.load_warnings}"
    )
    assert total < 2_000, (
        f"the load warnings total {total:,} characters. A diagnostic that "
        "embeds the refused VALUE materialises the structure the refusal "
        "prevented; every other warning in this module names a COORDINATE."
    )


# THE AST "CLASS" ARM WAS DELETED (`Inc-REPAIR` S-E review, MEDIUM-1).
#
# It forbade `!r` applied to a `Call`, and its docstring claimed "the defect
# cannot be rewritten elsewhere". The reviewer rewrote it TWICE and the arm
# stayed green: `d['name']!r` is a Subscript, a name bound to raw data is a
# Name, and `doc.name!r` -- WHICH WAS LIVE ON THE SAME LINE -- is an Attribute.
# `ast.Call` is one spelling of four, and `f"{repr(x)}"` uses no conversion at
# all.
#
# It was shape-based where the property is semantic, so it passed the fix and
# the reintroduced defect for the same reason. The structural arm below killed
# both rewrites at 261x in 0.02 s. An arm that names a class it does not cover
# is worse than no arm: it reads as coverage.


def scalar_amplified(payload: int = 50_000, dups: int = 200) -> str:
    """ONE anchor reused across many duplicate names -- no alias DEPTH at all.

    The code review fired this and it is worse than the bomb it replaced: a
    57 KB sidecar produced 19.9 MB of warnings in 0.081 SECONDS -- 348x
    amplification and CHEAP, so nothing times out. A type bound let it through
    because a huge `str` is an allowed type.
    """
    lines = ["_anchors:", f"  big: &big {'x' * payload}", "schema: []", "documents:"]
    for _ in range(dups):
        lines += ["  - name: *big", "    path: p.pdf"]
    lines += ["nodes:", "  raiz:", "    title: benigno", ""]
    return "\n".join(lines)


def test_llr_n13_1_7_a_huge_scalar_origin_is_bounded_too(tmp_path):
    """A TYPE bound is not a LENGTH bound.

    `_raw_origin` first admitted any scalar, and `AT-P02d` needs the origin
    shown so a coercion collision is distinguishable -- so the answer is
    truncation, not removal. Both halves of the record are bounded: `doc.name!r`
    was unbounded too, and being an Attribute rather than a Call, no AST arm
    shaped around `{call()!r}` could see it.
    """
    graph = _write(tmp_path, scalar_amplified()).load("m")

    assert any(w.startswith("documento duplicado:") for w in graph.load_warnings), (
        f"the duplicate record is missing entirely: {graph.load_warnings[:2]}"
    )
    total = sum(len(w) for w in graph.load_warnings)
    assert total < 200_000, (
        f"a 57 KB sidecar produced {total:,} characters of warnings. These are "
        "joined and coerced into an operator toast, so a megabyte of them is a "
        "per-character translate on the way to the screen."
    )


# THE SLOW TIMING ARM WAS DELETED (`Inc-REPAIR` S-E review, LOW-1).
#
# It asserted `elapsed < 5.0` on an 8-level sidecar. Fired, the mutants that
# reintroduce the defect reddened it at 5.0 s and 5.2 s -- a 0-4% margin, which
# on a faster machine or a warm cache goes GREEN against the defect it exists
# for. My own note called it "marginally red"; the measurement says that
# understated it.
#
# Neither alternative works: 9 levels is 54 s and falsifies `pyproject.toml`'s
# own declaration that no arm in either lane exceeds 20 s, and this defect's
# cost curve offers no point in between. A wall-clock arm should be reddened by
# an order of magnitude, not by 0.4%.
#
# The structural arm above kills the same mutants at 261x in 0.02 s,
# deterministically, in the DEFAULT lane. Keeping a weaker duplicate in a lane
# that runs less often is how a suite acquires arms nobody trusts.


# ---------------------------------------------------------------------------
# The coercion sink beside it


def test_coverage_screen_coerces_file_derived_text_with_plain():
    """`screens/coverage.py` used `escape`, and `escape` COERCES NOTHING.

    This batch measured that at `Inc-CRUMB`: four crumb producers reached the
    frame under `escape` alone, which guards markup and passes control
    characters, bidi overrides and zero-width joiners untouched. The standard is
    `darkside.plain`.

    Structural rather than behavioural because the claim is about which sink the
    module uses, and a rendered-frame assertion would pass the day someone adds
    a second unescaped call site beside a coerced one.
    """
    import mapper.screens.coverage as cov

    tree = ast.parse(Path(cov.__file__).read_text(encoding="utf-8"))
    escapes = [
        node.lineno for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "escape"
    ]
    assert not escapes, (
        f"coverage.py calls escape() at line(s) {escapes}. escape() guards "
        "markup and coerces nothing -- use darkside.plain, which this batch "
        "settled as the standard for file-derived text."
    )
