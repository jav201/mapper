"""HLR-GOLD.1 — the byte-identity pin census is DERIVED, and trigger `B3` is corrected.

THE DEFECT THIS CLOSES IS AN EVIDENCE DEFECT, NOT A CODE DEFECT.  Trigger `B3`
("the change touches a source a byte-identical golden captures") was recorded
`not_fired` on the probe `ls tests/goldens` -> no such directory.  **That probe was
correct as executed and its INPUT SET was wrong** (C-31): this repo keeps its
byte-identity pins in a module-level dict inside a test file, not in a `goldens/`
directory.  A non-activation with a false probe is indistinguishable from a trigger
nobody evaluated, which is exactly what C-48 exists to prevent.

The architect lens then reported **18** pins from a literal.  Derived here by
parsing the declaration, it is **12**.  A literal cannot notice a pin being added
or removed; a derivation reddens.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
DEPTH_TESTS = REPO / "tests" / "test_repair_depth.py"
STATE = REPO / ".dev-flow" / "state.json"


def _literal(name: str):
    """The value of a module-level literal assignment, read by parsing the source.

    Parsed rather than imported: importing `test_repair_depth` pulls in Textual and
    builds depth-5000 fixtures at collection time, which is a large cost to pay for
    reading two constants -- and it would couple this census to that module's
    import health.
    """
    tree = ast.parse(DEPTH_TESTS.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    raise AssertionError(f"{name} is not a module-level literal in {DEPTH_TESTS.name}")


def _census() -> dict:
    """(renderer, w, h) -> digest, derived from the declaration itself."""
    return _literal("MASTER_LEGACY_DIGESTS")


def _sizes() -> tuple:
    return _literal("GOLDEN_SIZES")


def _renderers() -> list[str]:
    return sorted({k[0] for k in _census()})


# --- TC-P06 / AT-P06: the census is derived and equals renderers x sizes -------


def test_tc_p06_the_pin_census_is_derived_not_asserted_from_a_literal():
    """AT-P06 -- the pin count is `len(renderers) x len(sizes)`, computed.

    The threshold is a PRODUCT, not the number 12.  Writing `== 12` would be the
    same defect as the architect lens's 18: a literal that stays green when a pin
    is added or removed, which is precisely what a census must not do.
    """
    census, sizes, renderers = _census(), _sizes(), _renderers()
    assert census, "the census is empty -- the declaration moved or stopped parsing"
    assert len(census) == len(renderers) * len(sizes), (
        f"{len(census)} pins is not {len(renderers)} renderers x {len(sizes)} sizes; "
        "the grid is incomplete, so some renderer is unpinned at some size"
    )
    # Every cell of the grid is present -- a product can match by coincidence while
    # one renderer is double-pinned and another missing a size.
    for renderer in renderers:
        for w, h in sizes:
            assert (renderer, w, h) in census, f"{renderer} is unpinned at {w}x{h}"


def test_tc_p06b_the_derived_count_is_twelve_and_the_literal_eighteen_is_wrong():
    """The measured reconciliation, recorded as an executed figure.

    This arm pins the CURRENT census size deliberately, as a regression pin rather
    than a gate (C-40's corollary): the arm above is the real check, and this one
    exists so the correction of the reported 18 is itself recorded in the suite.
    Adding a legitimate pin is expected to redden this and the number is updated.
    """
    assert len(_census()) == 12
    assert len(_renderers()) == 3 and len(_sizes()) == 4


def test_at_p06_radial_is_pinned_at_every_size_so_the_feature_batch_reddens_four():
    """AT-P06 -- `RadialRenderer` is pinned at all four sizes.

    This is the operative half for the FEATURE batch: its Inc-1 makes
    `Canvas.rows()` honour the `dots`/`bgs` layers, which is exactly what the
    radial view paints.  Those four pins therefore redden BY CONSTRUCTION -- an
    expected re-baseline, not a regression, and naming it here is what stops it
    surfacing as a surprise mid-increment (C-24).
    """
    census, sizes = _census(), _sizes()
    pinned = sorted((w, h) for (r, w, h) in census if r == "RadialRenderer")
    assert pinned == sorted(sizes), (
        f"RadialRenderer is pinned at {pinned}, not at all of {sorted(sizes)}"
    )


def test_tc_p06c_distinct_digests_are_fewer_than_pins_and_that_is_expected():
    """An observation that would otherwise read as a defect to the next reader.

    `OutlineRenderer` emits identical bytes at three of its four sizes, so 12 pins
    hold fewer than 12 distinct digests.  Recorded because a future reader counting
    distinct digests would otherwise think three pins had been lost.
    """
    census = _census()
    distinct = len(set(census.values()))
    assert distinct < len(census), (
        "every pin now has a distinct digest; the size-invariance of OutlineRenderer "
        "has changed and this note is stale"
    )
    assert distinct == 10, f"expected 10 distinct digests across 12 pins, got {distinct}"


# --- TC-P07 / AT-P07: the B3 non-activation record is corrected ----------------


def _triggers() -> dict:
    return json.loads(STATE.read_text(encoding="utf-8"))["triggers"]


def test_at_p07_trigger_b3_is_recorded_fired_and_not_merely_flipped():
    """AT-P07 -- `B3` is FIRED, and the record says WHY the first probe was wrong.

    C-48: a non-activation is evidence, so a FALSE non-activation is a defect in
    the evidence. Flipping the verdict without recording the reason would leave the
    next batch free to re-run the same `ls tests/goldens` probe and reach the same
    wrong answer.
    """
    triggers = _triggers()
    assert "B3" in triggers["fired"], "B3 is not recorded as fired"
    assert "B3" not in triggers["not_fired"], "B3 is in BOTH lists"

    corrections = {c["id"]: c for c in triggers.get("corrections", [])}
    assert "B3" in corrections, (
        "B3 was flipped to fired with no correction record; the reason the original "
        "probe was wrong is the part that stops it being re-run"
    )
    reason = corrections["B3"]["reason"]
    assert "input set" in reason.lower() or "INPUT SET" in reason, (
        f"the B3 correction does not name the input-set error: {reason!r}"
    )
    assert "MASTER_LEGACY_DIGESTS" in reason, (
        "the correction does not name where the pins actually live, so the next "
        f"reader cannot check it: {reason!r}"
    )


@pytest.mark.parametrize("field", ["fired", "not_fired"])
def test_tc_p07_the_trigger_record_is_well_formed(field):
    """Both lists must exist and be disjoint -- the record's own integrity."""
    triggers = _triggers()
    assert field in triggers, f"the trigger record has no {field!r} list"
    assert not (set(triggers["fired"]) & set(triggers["not_fired"])), (
        "a trigger appears in both fired and not_fired"
    )
