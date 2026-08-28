"""HLR-MAP.1 — `docs/ARCHITECTURE.md` describes the tree as it is.

The map is the ORACLE the A-family triggers read: a touched file is classified by
path prefix, so a stale or false map silently mis-classifies every future change.
That is why it gets a test at all — prose in a doc nobody executes is how the
previous amendment came to be recorded as landed while never touching disk (C-44).

TWO PROPERTIES, AND THEY ARE DIFFERENT:
  * AT-P04 — every path the map DECLARES IT OWNS exists on disk.
  * AT-P05 — the map makes no present-tense claim about a symbol absent from the
    tree.

THE SCOPING IS THE WHOLE DIFFICULTY.  A naive "every path-like string in the file
must exist" reddens on `mapper/screens/prompt.py`, which the map mentions as a
PROPOSED REMEDIATION TARGET for a recorded import-cycle violation, and on
`mapper/views/state.py`, which is an explicitly-marked forward COMMITMENT.  Both
are correct as written.  A checker that flags them would false-fail correct work,
which costs exactly as much as passing wrong work (C-53) and trains everyone to
ignore the check.  So the oracle reads the OWNED-PATHS COLUMN of the composition
table, which is the part the triggers actually consume.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
MAP = REPO / "docs" / "ARCHITECTURE.md"


def _composition_rows() -> list[tuple[str, str]]:
    """(module, paths-cell) for every row of the composition table.

    Derived by parsing the table, not hand-listed: a module added to the map is
    picked up automatically, which is the property that makes this an oracle
    rather than a snapshot of what someone remembered (C-31).
    """
    rows: list[tuple[str, str]] = []
    in_table = False
    for line in MAP.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Module | Paths it owns |"):
            in_table = True
            continue
        if in_table:
            if not line.startswith("|"):
                break
            if set(line) <= set("|- "):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 2:
                rows.append((cells[0].strip("`"), cells[1]))
    return rows


def _declared_paths() -> list[tuple[str, str]]:
    """(module, path) for every path the composition table says a module OWNS."""
    out: list[tuple[str, str]] = []
    for module, cell in _composition_rows():
        for raw in re.findall(r"`([^`]+)`", cell):
            if "/" in raw or raw.endswith(".py"):
                out.append((module, raw))
    return out


def test_tc_p05_the_composition_table_is_parseable_and_non_degenerate():
    """The derivation must be able to report a NON-absence, or its greens are void.

    If the table's header is ever reworded, `_declared_paths()` returns `[]` and
    every parametrized arm below vanishes -- a suite with zero arms reports green.
    An arm the harness cannot see is an arm it cannot report inert (C-55).
    """
    rows = _composition_rows()
    paths = _declared_paths()
    assert len(rows) >= 15, f"parsed only {len(rows)} module rows; the table moved"
    assert len(paths) >= 15, f"parsed only {len(paths)} owned paths"
    modules = {m for m, _ in rows}
    for expected in ("model", "store", "canvas", "views", "app"):
        assert expected in modules, f"module {expected!r} vanished from the map"


@pytest.mark.parametrize(
    "module,declared", _declared_paths(), ids=lambda v: v if isinstance(v, str) else v
)
def test_at_p04_every_owned_path_exists_on_disk(module, declared):
    """AT-P04 -- a path the map claims a module OWNS must exist.

    This is the arm that would have caught the un-landed ARQ amendment: the map
    can only classify a touched file if the prefixes it declares are real.
    """
    matches = list(REPO.glob(declared))
    assert matches, (
        f"module {module!r} declares it owns {declared!r}, which matches nothing on "
        "disk -- the map cannot classify a file under a path that does not exist"
    )


# The symbols the map asserted in the PRESENT TENSE and the tree does not have.
# Each was executed against disk at `d877784`; each is now either corrected or
# marked as a forward commitment.  This arm is a REGRESSION PIN on those specific
# corrections -- it does not claim to find new ones, and it is labelled so rather
# than left to read as a general guarantee (C-40's corollary).
#
# CONSTRAINT ON THE MAP'S OWN PROSE, learned by tripping over it: a correction note
# may DESCRIBE the claim it replaced but must not SPELL it verbatim, because this
# pin cannot tell a value being reported from one being declared.  The first draft
# of the `search` note quoted the old constructor signature and reddened its own
# arm.  This is C-56 -- an evidence transcript is corpus input -- and the remedy is
# C-56's: describe by position and operation, never paste the token.
_CORRECTED_FALSEHOODS = {
    "Canvas.dline": "`Canvas(w, h)` with `put`, `wire`, `edge`, `elbow_down`, `text`, `dline`",
    "public MapStore.reindex": "`save(map_id, graph, sidecar)`, `reindex()`",
    "load returning a tuple": "`load(map_id) -> (Graph, Sidecar)`",
    "Canvas.rows returning str": "`rows() -> list[str]`",
    "SearchIndex taking a store": "`SearchIndex(store)`",
}


@pytest.mark.parametrize("label", sorted(_CORRECTED_FALSEHOODS))
def test_at_p05_a_corrected_falsehood_has_not_returned(label):
    """AT-P05 -- the six false claims stay corrected.

    Verbatim-substring pins.  Deliberately narrow: they certify that THESE
    corrections survive, not that the map is true in general.  Calling them a
    general truth check would be the same false record the amendment was fixing.
    """
    text = MAP.read_text(encoding="utf-8")
    stale = _CORRECTED_FALSEHOODS[label]
    assert stale not in text, (
        f"the map has regressed to the false claim {label!r} ({stale!r}); it was "
        "executed against disk and does not hold"
    )


def test_at_p05b_a_forward_commitment_is_never_written_present_tense():
    """A committed-but-unbuilt contract must be MARKED, not asserted.

    The ARQ proposal declared `mapper/views/state.py` "new this batch" for a file
    that does not exist.  Landing that verbatim would have traded a C-44 defect
    (work recorded as done that never landed) for a false map -- and the map is
    the oracle the triggers read.

    DISCHARGED 2026-08-28 in `2026-08-26-ui-next-batch-02` Inc-2: the file
    landed, so the commitment became a fact and the map says so.  The guard is
    kept and INVERTED rather than deleted -- it now asserts the row is NOT still
    marked as a forward commitment, which is the direction that can go wrong
    from here.  A guard whose condition has been satisfied is not spent; it is
    the thing that stops the row regressing into a promise again.

    ANCHORED ON THE ROW, and the first attempt was not.  That version split the
    whole document on the first occurrence of the filename and read 400
    characters after it -- but the first occurrence is in this file's prose
    preamble, 131 lines above the row, so the window never reached the thing it
    claimed to check.  Executed against the BASELINE document, in which the row
    still read COMMITTED: the guard PASSED.  It had replaced a live assertion
    with one that could not fail, which is worse than having deleted it.
    """
    text = MAP.read_text(encoding="utf-8")
    assert (REPO / "mapper" / "views" / "state.py").exists(), (
        "mapper/views/state.py landed in Inc-2 and must not vanish"
    )
    row = next(
        (line for line in text.splitlines()
         if line.startswith("| **`ViewState` parameter object**")),
        None,
    )
    assert row is not None, "the ViewState row is gone from the module map"
    # Match the CONCEPT, not one phrasing.  Pinning the exact string
    # "COMMITTED, NOT PRESENT" let the identical regression through under the
    # shorter "NOT PRESENT" -- and the backstop below was satisfied by the
    # PRESENT *inside* NOT PRESENT, which made it near-vacuous.
    assert "NOT PRESENT" not in row and "NOT YET IN THE TREE" not in row, (
        "`mapper/views/state.py` exists on disk, so its row must be present "
        "tense; leaving it marked as a forward commitment makes the map -- the "
        "oracle the A-family triggers read -- assert something false"
    )
    assert "· **PRESENT**" in row
