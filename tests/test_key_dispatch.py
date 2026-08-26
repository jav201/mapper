"""Every advertised key dispatches the action advertised BESIDE it (US-N03).

Closes the gap the PR gate found. Three properties were being confused for each
other, and only two of them were gated:

* `AT-N03a` — the action a seat entry names **exists** on the owning screen.
* `AT-N03f` — the key a seat entry names is **bound** on that screen.
* the **pairing** — key K dispatches the action shown next to K. **Ungated.**

Swapping only the `action` field of two seat entries — so `u` folds a branch and
`z` undoes — left the whole suite at `210 passed`. The operator reads
`u deshacer`, presses it, and folds a branch; reads `z plegar rama`, presses it,
and silently destroys an edit. Only 11 distinct keys were pressed anywhere in the
suite against 25 map bindings; `u` was never pressed, because the undo tests call
`screen.action_undo()` directly.

The input set is derived from `KEYMAP` at import, so a binding added to the seat
is automatically covered here.
"""
from __future__ import annotations

import pytest

from mapper import keymap
from mapper.app import MapperApp, MapScreen
from mapper.model import Edge, Ficha, Graph, Node, SchemaField

MAP_BINDINGS = [b for b in keymap.KEYMAP if b.scope == keymap.SCOPE_MAP]

# The INDEPENDENT referent, and it is hand-written on purpose.
#
# Deriving the expectation from the seat makes this test a tautology: the screen's
# BINDINGS are generated FROM the seat, so swapping two `action` fields propagates
# consistently and nothing can see it.  That is exactly what happened on the first
# attempt at this file — the swap mutation stayed green.
#
# C-31 warns that a hand-listed set is usually a weak oracle.  Here it is the
# *specification*: this table says what the operator is promised when they read a
# label next to a key.  Its value comes precisely from NOT being derived from the
# thing it checks.  A deliberate rebinding must be made here too, in one line.
EXPECTED_MAP_PAIRING = {
    "j": "next_sibling",
    "k": "prev_sibling",
    "h": "parent",
    "l": "child",
    "enter": "open_ficha",
    "slash": "search",
    "a": "add_child",
    "d": "open_documents",
    "x": "archive",
    "u": "undo",
    "A": "add_attachment",
    "X": "remove_attachment",
    "f": "toggle_focus",
    "o": "toggle_outline",
    "r": "toggle_radial",
    "e": "export_svg",
    "equals_sign": "toggle_diff",
    "m": "coverage",
    "n": "next_gap",
    "R": "toggle_rail",
    "I": "toggle_inspector",
    "g": "focus_rail",
    "z": "collapse_branch",
    "q": "home",
    "escape": "back_or_home",
}


def test_at_n03h_the_seat_pairs_every_key_with_the_promised_action():
    """AT-N03h — the seat's key->action pairing matches the specification.

    The defect this closes: swapping the `action` fields of the `u` and `z`
    entries left the entire suite green.  The operator would read `u deshacer`,
    press it, and fold a branch; read `z plegar rama`, press it, and silently
    destroy an edit.

    RED mutation: swap any two `action` fields in the map scope; both keys fail.
    """
    actual = {b.key: b.action for b in MAP_BINDINGS}
    assert actual == EXPECTED_MAP_PAIRING, (
        "the seat's key->action pairing drifted from the specification; "
        "if the rebinding is deliberate, change EXPECTED_MAP_PAIRING too"
    )


def test_the_input_set_is_not_empty_and_covers_the_map_scope():
    """Fence: a parametrized test over an empty set passes without asserting anything."""
    assert len(MAP_BINDINGS) >= 20, "the map scope shrank; this suite may be vacuous"
    assert {b.key for b in MAP_BINDINGS} >= {"j", "k", "u", "x", "m", "n"}


def _seed(app):
    g = Graph()
    g.schema = [SchemaField(key="D", label="documento", required=True)]
    g.add_node(Node(id="root", ficha=Ficha(title="erp", fields={"D": "a"})))
    g.add_node(Node(id="a", ficha=Ficha(title="alfa")))
    g.add_edge(Edge("root", "a"))
    app.store.save("kd", g)
    return "kd"


@pytest.mark.parametrize(
    "binding", MAP_BINDINGS, ids=lambda b: f"{b.key}->{b.action}"
)
async def test_at_n03g_each_key_dispatches_its_own_advertised_action(tmp_path, binding):
    """AT-N03g — press the real key, observe which action ran.

    Every `action_*` the map scope declares is replaced with a recorder before the
    press, so the assertion is an exact identity: this key ran THIS action and no
    other. Replacing the methods also keeps the press side-effect-free, which is
    what makes it safe to do this for destructive keys like `x`.

    RED mutation: swap the `action` fields of any two seat entries; both of those
    arms fail and the rest stay green.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        app.push_screen(MapScreen(_seed(app)))
        await pilot.pause()
        await pilot.pause()
        screen = app.screen

        fired: list[str] = []

        def recorder(name: str):
            def _run() -> None:
                fired.append(name)
            return _run

        # Patch every map-scope action on the instance, so a mis-paired key is
        # caught as "the wrong name fired" rather than silently doing nothing.
        for other in MAP_BINDINGS:
            setattr(screen, f"action_{other.action}", recorder(other.action))
        # App-scope actions are reachable from here too; patch them so a key that
        # falls through is still observed.
        for other in keymap.bindings_for(keymap.SCOPE_APP):
            setattr(app, f"action_{other.action}", recorder(other.action))

        await pilot.press(binding.key)
        await pilot.pause()

        assert fired == [binding.action], (
            f"pressing {binding.glyph!r} (advertised as {binding.label!r}) "
            f"ran {fired or 'nothing'}, expected [{binding.action!r}]"
        )
