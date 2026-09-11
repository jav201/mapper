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
import time
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
        "  n:",
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

    for phantom in ("fantasma", "segundo_fantasma"):
        assert any(phantom in w for w in graph.load_warnings), (
            f"the sidecar declares {phantom!r}, which the .mmd does not define, "
            f"and no load warning names it. Warnings: {graph.load_warnings}"
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
    for marker in ("\\", "/", ".mmd"):
        assert marker not in message, (
            f"the message carries a filesystem detail {marker!r}: {message!r}"
        )


# ---------------------------------------------------------------------------
# B-48 — the attachments phantom


def test_b48_a_mapping_without_attachment_keys_is_refused_not_invented(tmp_path):
    """`attachments` validates TYPE but not CONTENT.

    A scalar entry is correctly refused with a warning. A MAPPING carrying none
    of the attachment keys is accepted SILENTLY as an `Attachment` with empty
    kind, path and caption -- so nothing is lost and a phantom is INVENTED.

    `store.py`'s own comment records that malformed attachments used to be
    discarded silently and that this was fixed. The fix covers scalars and not
    mappings, which is a declaration outrunning the code.
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
    empty = [a for a in attachments if not a.kind and not a.path and not a.caption]
    assert not empty, (
        f"{len(empty)} attachment(s) were INVENTED from a mapping with no "
        "attachment keys -- empty kind, path and caption, and no warning. "
        f"Warnings: {graph.load_warnings}"
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

    assert total < 2_000, (
        f"the load warnings total {total:,} characters. A diagnostic that "
        "embeds the refused VALUE materialises the structure the refusal "
        "prevented; every other warning in this module names a COORDINATE."
    )


def test_llr_n13_1_7_no_warning_interpolates_a_raw_sidecar_value():
    """The CLASS, not the site -- so the defect cannot be rewritten elsewhere.

    Every diagnostic in `store.py` names a coordinate: `{owner}.{key}`,
    `{owner}.{key}[{i}]`, `{nid}.fields`. The `!r` conversions are applied to
    KEYS and IDS, which are short by construction.

    A `!r` applied to a CALL -- `d.get('name')!r` -- reads raw sidecar data of
    unknown size and shape. That is the one site the defect lived at, and this
    forbids the shape rather than the instance.
    """
    import mapper.store as store_mod

    tree = ast.parse(Path(store_mod.__file__).read_text(encoding="utf-8"))
    offenders = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.FormattedValue)
        and node.conversion == ord("r")
        and isinstance(node.value, ast.Call)
    ]
    assert not offenders, (
        f"store.py interpolates a CALL with !r at line(s) {offenders}. That "
        "reads raw sidecar data of unbounded size into a diagnostic -- name the "
        "coordinate instead, as every other warning here does."
    )


@pytest.mark.slow
def test_llr_n13_1_7_an_amplified_sidecar_loads_in_bounded_time(tmp_path):
    """The end-to-end number, where wall-clock asserts belong.

    EIGHT levels, not nine: nine measures 54 s and `pyproject.toml` declares
    that the slowest arm in either lane is under 20 s. An arm that falsifies the
    declaration it runs under is the defect this batch keeps cataloguing, so the
    depth was chosen by measurement -- 8 levels is 5.3 s on the shipped tree,
    which is unambiguous and keeps the declaration true.
    """
    start = time.perf_counter()
    graph = _write(tmp_path, amplified(levels=8)).load("m")
    elapsed = time.perf_counter() - start

    assert elapsed < 5.0, (
        f"an alias-amplified sidecar took {elapsed:.1f} s to load. Measured on "
        "the shipped tree: 5.3 s at this depth, 54 s one level deeper, against "
        "0.02 s for the benign equivalent."
    )
    assert sum(len(w) for w in graph.load_warnings) < 2_000


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
