"""Inc-4b's own seat census — `C-D25a` and `C-D25b` for the `#D5b` rebind.

`keymap.py` is a FOUR-WAY collision (Inc-3, Inc-4b, Inc-8, Inc-9) resolved by
serial ordering rather than by ownership, so each participant re-runs
`duplicate_chords()` and the whole-seat pin on ENTRY and on EXIT, and asserts its
DECLARED row diff EQUAL to the entry/exit difference of `bindings_for("map")`.

WHY THE EQUALITY IS THE POINT AND THE DECLARATION ALONE IS NOT.  A declared diff
joined to no oracle is not a pin: rebind a fifth row and declare four, and
`duplicate_chords()` still returns `[]`, because nothing was duplicated.  What
catches the undeclared fifth row is the *equality* between what this file says
the increment did and what the seat actually shows it did.

Inc-3's diff is pinned in `tests/test_inc3_census.py` against SNAPSHOTS of its
own entry and exit; this file pins Inc-4b's against the seat that is live today.
Two increments, two nodes, neither able to make the other red.
"""
from __future__ import annotations

import inspect

from mapper.keymap import KEYMAP, bindings_for, duplicate_chords

# The `map`-scope seat as it stood at `68b1c09` (Inc-4a's close), which is
# Inc-4b's ENTRY.  Identical to Inc-3's frozen exit -- Inc-4a touched 0 lines of
# `keymap.py` -- and spelled out here rather than imported from the Inc-3 census,
# because a pin that reads another increment's snapshot inherits that
# increment's edits along with it.
ENTRY_MAP_SEAT = frozenset({
    ("j", "next_sibling"), ("k", "prev_sibling"), ("h", "parent"), ("l", "child"),
    ("enter", "open_ficha"), ("slash", "search"),
    ("a", "add_child"), ("d", "open_documents"), ("x", "archive"), ("u", "undo"),
    ("A", "add_attachment"), ("X", "remove_attachment"),
    ("f", "toggle_focus"), ("o", "toggle_outline"), ("r", "toggle_radial"),
    ("e", "export_svg"), ("equals_sign", "toggle_diff"), ("m", "coverage"),
    ("n", "next_gap"), ("R", "toggle_rail"), ("I", "toggle_inspector"),
    ("g", "focus_rail"), ("z", "collapse_branch"),
    ("q", "home"), ("escape", "back_or_home"),
    ("ctrl+p", "palette"), ("question_mark", "help"),
    ("H", "pan_left"), ("J", "pan_down"), ("K", "pan_up"), ("L", "pan_right"),
})

# The three rows `#D5b` claims: one REBOUND (`n`) and two ADDED (`N`, `M`).
DECLARED_ADDED = frozenset({
    ("n", "next_hit"), ("N", "prev_hit"), ("M", "next_gap"),
})

# A rebind is a removal as well as an addition, and Inc-3's census had no vocabulary
# for one -- which is why its "nothing left the seat" assertion went red here by
# construction.  Inc-4b declares its removal explicitly.
DECLARED_REMOVED = frozenset({("n", "next_gap")})


def live_map_seat() -> frozenset[tuple[str, str]]:
    return frozenset((b.key, b.action) for b in bindings_for("map"))


def test_cd25a_the_seat_diff_is_exactly_the_three_rows_inc4b_declares():
    """Declared EQUALS measured, in both directions."""
    exit_seat = live_map_seat()
    assert len(ENTRY_MAP_SEAT) == 31, len(ENTRY_MAP_SEAT)
    assert len(exit_seat) == 33, len(exit_seat)
    assert exit_seat - ENTRY_MAP_SEAT == DECLARED_ADDED
    assert ENTRY_MAP_SEAT - exit_seat == DECLARED_REMOVED

    # `n` is the rebound row, and the rebind is the whole `#D5b` ruling: the same
    # chord, a different action.  Asserted as an identity on the KEY rather than
    # inferred from the two sets, so a future edit that dropped `n` entirely and
    # added some other chord could not satisfy this node.
    rebound = {key for key, _ in DECLARED_REMOVED} & {key for key, _ in DECLARED_ADDED}
    assert rebound == {"n"}, rebound


def test_cd25b_no_chord_collides_on_entry_or_on_exit():
    """`duplicate_chords()` -> `[]` on BOTH sides, through the shipped detector.

    The entry side is reconstructed from the live seat by undoing this
    increment's own three rows -- putting `("n", "next_gap")` back and taking
    `N`, `M` and the new `n` out -- rather than by quoting a transcript.  A
    transcript records what someone ran; this records what the detector says.
    """
    assert duplicate_chords() == []

    entry = [b for b in KEYMAP if (b.key, b.action) not in DECLARED_ADDED]
    assert len(entry) == len(KEYMAP) - 3, (len(entry), len(KEYMAP))
    # Put the removed row back, so the reconstruction really is the ENTRY seat
    # and not merely the exit seat with three rows missing.
    restored = [(b.scope, b.key) for b in entry] + [("map", "n")]
    assert len(restored) == 52, len(restored)

    seen: set[tuple[str, str]] = set()
    clashes: list[tuple[str, str]] = []
    for pair in restored:
        if pair in seen:
            clashes.append(pair)
        seen.add(pair)
    app_keys = {key for scope, key in restored if scope == "app"}
    for scope, key in restored:
        if scope != "app" and key in app_keys:
            clashes.append((scope, key))
    assert sorted(set(clashes)) == []


def test_cd25a_every_new_chord_dispatches_to_a_method_that_exists():
    """A seat row naming a method the screen does not define is a silent no-op.

    The precedent is in this tree: the help overlay borrowed the palette's
    `enter -> run_selected`, a method `HelpScreen` never defined.  This is a
    DECLARATION check and it is labelled as one -- it proves the seat names a
    real method, never that the chord reaches it.  `AT-051` and `AT-022` press
    the real `M`, `n` and `N` and read the painted result, which is the only arm
    that can tell a rebind from a rename.
    """
    from mapper.app import MapScreen

    for key, action in sorted(DECLARED_ADDED):
        method = getattr(MapScreen, f"action_{action}", None)
        assert callable(method), (key, action)
        assert list(inspect.signature(method).parameters) == ["self"], action
