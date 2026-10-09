"""Seat-diff census of the data-safety batch (2026-10-08), design E-7.

The older census nodes that read the live seat (`test_inc9.py`
`test_cd25a_the_seat_diff_is_exactly_what_inc9_declares`, and from Inc-1b
`test_inc4_census.py`) are statements about THEIR increment.  They subtract the
rows declared here instead of widening their own lists, and this module is the one
place that pins those rows against the live `KEYMAP` in both directions, so a
subtracted row can never be a row that is not there.

Inc-1a declares the three `draft` rows.  Inc-1b adds `("map", "ctrl+s",
"save_draft")` to this set in the same edit as the seat row.
"""
from __future__ import annotations

from mapper import keymap

DATA_SAFETY_ADDED = frozenset({
    ("draft", "s", "save"),
    ("draft", "d", "discard"),
    ("draft", "escape", "stay"),
})


def test_every_declared_row_is_in_the_live_seat():
    """The subtraction in the older census nodes is only honest if each subtracted
    row exists.  A row removed from the seat but left here would hide a loss."""
    live = {(b.scope, b.key, b.action) for b in keymap.KEYMAP}
    assert DATA_SAFETY_ADDED <= live, sorted(DATA_SAFETY_ADDED - live)


def test_the_draft_scope_is_exactly_the_declared_rows():
    """Declared EQUALS measured for the whole `draft` scope: a fourth row, or a
    rebound one, reddens here rather than being absorbed by the subtraction."""
    live = {(b.scope, b.key, b.action) for b in keymap.KEYMAP if b.scope == keymap.SCOPE_DRAFT}
    declared = {row for row in DATA_SAFETY_ADDED if row[0] == keymap.SCOPE_DRAFT}
    assert len(declared) == 3
    assert live == declared


def test_the_draft_scope_is_modal_and_borrows_no_chord():
    """LLR-003.1: the guard is a modal, so it inherits no app chord (a modal that
    rebound `ctrl+p` would reopen the palette on top of itself), and no row is
    `priority` (the guard must not steal a key from a focused field underneath)."""
    assert keymap.SCOPE_DRAFT in keymap.MODAL_SCOPES
    rows = keymap.bindings_for(keymap.SCOPE_DRAFT)
    assert [(b.key, b.action) for b in rows] == [("s", "save"), ("d", "discard"), ("escape", "stay")]
    assert not any(b.priority for b in rows)
    assert keymap.duplicate_chords() == []


def test_the_draft_group_is_declared_before_app_and_headed_unsaved():
    """`bar_group_order` keeps `app` last only if `draft` is inserted before it."""
    assert keymap.GROUP_SCOPE["draft"] == keymap.SCOPE_DRAFT
    assert keymap.group_header("draft") == "unsaved"
    assert list(keymap.GROUP_SCOPE)[-1] == "app"
    assert keymap.bar_group_order(keymap.SCOPE_MAP)[-1] == "app"
