"""Tests for the single keymap seat (US-N03).

The load-bearing test here is `test_at_n03a_*`: it certifies a UNIVERSAL — that
*every* binding the seat declares resolves to an action the owning screen really
defines.  A universal is only as strong as the set it quantifies over, so the set
is derived from `KEYMAP` at import time and fenced by an explicit completeness
guard.  A hand-listed set would survive every code mutation and prove nothing.
"""
from __future__ import annotations

import inspect

import pytest

from mapper import keymap
from mapper.app import (
    HomeScreen,
    MapperApp,
    MapScreen,
    PlugRepoScreen,
    RepoScreen,
    _ImportPreviewScreen,
)
from mapper.keymap import GROUP_SCOPE, KEYMAP, bindings_for, groups_for_keybar, palette_items
from mapper.screens.help import HelpScreen
from mapper.screens.palette import CommandPalette

# Which class owns each scope's actions.  App-scope actions live on the App and are
# reachable from every screen by fall-through.
SCOPE_OWNER = {
    keymap.SCOPE_HOME: HomeScreen,
    keymap.SCOPE_MAP: MapScreen,
    keymap.SCOPE_REPO: RepoScreen,
    keymap.SCOPE_PLUG: PlugRepoScreen,
    keymap.SCOPE_IMPORT: _ImportPreviewScreen,
    keymap.SCOPE_PALETTE: CommandPalette,
    keymap.SCOPE_HELP: HelpScreen,
    keymap.SCOPE_APP: MapperApp,
}

# Per-scope sizes, pinned EXACTLY.  A `>=` fence leaves slack, and slack is
# invisible: with `len(KEYMAP) >= 33` against 39 declared, six map bindings could
# be deleted and the suite still reported 126 passed / 0 failed — the palette
# quietly lost `f`, `o`, `r`, `e`, `=` and `x` while every assertion held.  The
# only signal was a passing-test count that nothing asserted.  Changing the seat
# must now be a deliberate edit here.
EXPECTED_PER_SCOPE = {
    keymap.SCOPE_HOME: 11,
    keymap.SCOPE_MAP: 25,
    keymap.SCOPE_REPO: 3,
    keymap.SCOPE_PLUG: 1,
    keymap.SCOPE_IMPORT: 2,
    keymap.SCOPE_PALETTE: 2,
    keymap.SCOPE_HELP: 2,
    keymap.SCOPE_APP: 2,
}

# Derived from the live module, never hand-listed (control C-31).
ALL_BINDINGS = list(KEYMAP)


def test_keymap_completeness_guard():
    """Fence the input set of the conformance tests below.

    Without an exact fence, shrinking `KEYMAP` shrinks the universal along with
    it: fewer cases, still zero failures, green suite, degraded palette.
    """
    actual = {scope: 0 for scope in SCOPE_OWNER}
    for b in ALL_BINDINGS:
        actual[b.scope] += 1
    assert actual == EXPECTED_PER_SCOPE, "the seat changed size; update this fence deliberately"
    assert len(ALL_BINDINGS) == sum(EXPECTED_PER_SCOPE.values())
    assert {b.scope for b in ALL_BINDINGS} == set(SCOPE_OWNER), "a scope has no owning class"
    for b in ALL_BINDINGS:
        assert b.key and b.glyph and b.action and b.label and b.group, f"blank field in {b}"
        assert b.action.isidentifier(), f"{b.action!r} is not a method-name stem"
        assert b.group in GROUP_SCOPE, f"group {b.group!r} maps to no scope"


@pytest.mark.parametrize("binding", ALL_BINDINGS, ids=lambda b: f"{b.scope}:{b.key}:{b.action}")
def test_at_n03a_every_binding_resolves_to_a_real_action(binding):
    """AT-N03a — every seat entry dispatches to an action the owner really defines.

    This replaces `test_palette_dispatches_selected_action`, which searched the
    palette for "add", matched nothing (every label was Spanish prose), dismissed
    with None, and then asserted the palette had closed — which was true precisely
    BECAUSE nothing dispatched.  It passed on a completely broken palette.
    """
    owner = SCOPE_OWNER[binding.scope]
    method_name = f"action_{binding.action}"
    assert hasattr(owner, method_name), (
        f"{owner.__name__} has no {method_name} for {binding.glyph!r} ({binding.label})"
    )
    # `hasattr` alone is too weak: Textual's Screen base supplies action_focus,
    # action_toggle, action_blur and friends, so an entry pointing at inherited
    # framework plumbing would pass while doing nothing this app intends.
    method = getattr(owner, method_name)
    defining_module = getattr(inspect.unwrap(method), "__module__", "")
    assert defining_module.startswith("mapper."), (
        f"{method_name} on {owner.__name__} is inherited from {defining_module},"
        " not defined by this application"
    )


@pytest.mark.parametrize("scope", sorted(SCOPE_OWNER))
def test_at_n03f_bound_keys_match_the_seat_exactly(scope):
    """AT-N03f — what each screen really BINDS equals what the seat declares.

    The conformance test above checks the `action` field only, so corrupting a
    `key` or a `glyph` left the whole suite green while help, the palette and the
    keybar all advertised a chord that does nothing.  This closes that: it reads
    the bindings Textual actually merged onto the class.
    """
    owner = SCOPE_OWNER[scope]
    # Textual contributes bindings of its own (focus traversal, copy, ctrl+q quit).
    # Subtract whatever the BASE class already binds — derived from the framework
    # at runtime, not a hand-listed allowance that would rot silently.
    inherited = set(owner.__mro__[1]._merged_bindings.key_to_bindings)
    bound = set(owner._merged_bindings.key_to_bindings) - inherited
    expected = {b.key for b in keymap.bindings_for(scope)}
    assert bound == expected, (
        f"{owner.__name__} binds {bound - expected} that the seat does not declare, "
        f"and is missing {expected - bound} that it does"
    )


def test_glyph_is_a_plausible_display_form_of_its_key():
    """A corrupted glyph advertises a chord that does nothing; nothing else catches it."""
    display = {
        "enter": "↵", "escape": "esc", "slash": "/",
        "equals_sign": "=", "question_mark": "?",
    }
    for b in ALL_BINDINGS:
        expected = display.get(b.key, b.key)
        assert b.glyph == expected, f"{b.key} is displayed as {b.glyph!r}, expected {expected!r}"


def test_no_duplicate_chord_inside_one_scope():
    """LLR-N03.6 — a chord bound twice in one scope means one action can never fire."""
    assert keymap.duplicate_chords() == []


def test_duplicate_chords_actually_detects_a_duplicate(monkeypatch):
    """The positive control for the test above.

    Asserting `== []` against a clean seat never executes the detector: gutting
    its body to `return []` left the suite fully green.  This drives a synthetic
    seat that really does contain a collision, so the detector has to work.
    """
    clash = keymap.KeyBinding("m", "m", "toggle_outline", "duplicado", "view")
    monkeypatch.setattr(keymap, "KEYMAP", list(KEYMAP) + [clash])
    assert keymap.duplicate_chords() == [("map", "m")]
    # ...and a same chord in a DIFFERENT scope is legitimate, not a clash.
    other = keymap.KeyBinding("m", "m", "consult", "otro scope", "doors")
    monkeypatch.setattr(keymap, "KEYMAP", list(KEYMAP) + [other])
    assert keymap.duplicate_chords() == []


def test_no_seat_entry_binds_tab():
    """LLR-N06.5, seat half — `tab` belongs to focus traversal."""
    assert [b for b in KEYMAP if b.key == "tab"] == []


def test_llr_n06_5_no_screen_binds_tab_outside_the_recorded_exceptions():
    """LLR-N06.5, tree half — the universal the seat half only looked like.

    A screen-level `tab` binding was measured to produce 0 focus moves in 9
    presses, which would leave the inspector keyboard-unreachable.  Two unmigrated
    modal screens still bind it; they are named in `TAB_BINDING_EXCEPTIONS` so a
    NEW one reddens this test instead of passing unnoticed.
    """
    import inspect as _inspect

    from textual.screen import Screen

    from mapper import app as app_module
    from mapper.screens import coverage, editor, factory, help as help_mod, palette, settings

    offenders = []
    for module in (app_module, coverage, editor, factory, help_mod, palette, settings):
        for _, cls in _inspect.getmembers(module, _inspect.isclass):
            if not issubclass(cls, Screen) or cls.__module__ != module.__name__:
                continue
            keys = {
                b[0] if isinstance(b, tuple) else b.key
                for b in (cls.__dict__.get("BINDINGS") or [])
            }
            if "tab" in keys and cls.__name__ not in keymap.TAB_BINDING_EXCEPTIONS:
                offenders.append(cls.__name__)
    assert offenders == [], f"screens binding tab outside the recorded exceptions: {offenders}"


def test_tab_binding_exceptions_are_still_real():
    """Fence the exception list: a stale exception hides a regression.

    If one of these screens stops binding `tab`, the exception must go — otherwise
    it silently licenses a future `tab` binding on that screen.
    """
    import inspect as _inspect

    from mapper.screens import editor, settings

    for module in (editor, settings):
        for _, cls in _inspect.getmembers(module, _inspect.isclass):
            if cls.__name__ not in keymap.TAB_BINDING_EXCEPTIONS:
                continue
            keys = {
                b[0] if isinstance(b, tuple) else b.key
                for b in (cls.__dict__.get("BINDINGS") or [])
            }
            assert "tab" in keys, f"{cls.__name__} no longer binds tab; retire the exception"


def test_bindings_for_includes_app_scope_but_not_other_screens():
    map_actions = {b.action for b in bindings_for(keymap.SCOPE_MAP)}
    assert "next_sibling" in map_actions
    assert "palette" in map_actions, "app-scope keys are reachable from every screen"
    assert "consult" not in map_actions, "home-scope keys must not leak into map scope"


def test_groups_for_keybar_order_and_glyphs():
    groups = groups_for_keybar(["nav", "app"])
    assert [g[0] for g in groups] == ["nav", "app"]
    nav_pairs = groups[0][1]
    assert ("j", "siguiente") in nav_pairs
    # The keybar shows the glyph, never the Textual key name.
    assert ("↵", "abrir ficha") in nav_pairs
    assert not any(k == "enter" for k, _ in nav_pairs)


def test_palette_items_filters_by_scope_and_query():
    map_items = palette_items("", keymap.SCOPE_MAP)
    assert all(b.scope in {keymap.SCOPE_MAP, keymap.SCOPE_APP} for b in map_items)
    hits = palette_items("cobertura", keymap.SCOPE_MAP)
    assert [b.action for b in hits] == ["coverage"]
    # A query matching nothing returns nothing rather than everything.
    assert palette_items("zzzzz", keymap.SCOPE_MAP) == []
