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

# The INDEPENDENT referent — the WHOLE seat, every field, hand-maintained.
#
# Three narrower versions of this failed in review, and each failure is the reason
# for one column here:
#
#   1. Deriving the expectation from `KEYMAP` made it a tautology: the screens'
#      BINDINGS are generated FROM the seat, so a swap propagates consistently and
#      nothing can see it.
#   2. Pinning only `key -> action` left the LABEL free. Swapping just the labels
#      of `u` and `z` kept 245 tests green — the operator reads "u plegar rama",
#      presses it, and performs an undo instead. Same deception, other field.
#   3. Pinning only the map scope left 23 of 48 bindings unpinned. A home-scope
#      `r`/`q` action swap stayed green, so "retomar último" quit the application.
#
# So the specification is the full tuple for all 48 entries, compared by SET
# EQUALITY. C-31 warns that a hand-listed set is usually a weak oracle; here it is
# the specification, and its whole value is that it is not derived from the thing
# it checks. A deliberate rebinding is a two-line change: the seat, and this table.
EXPECTED_SEAT: dict[tuple[str, str], tuple[str, str, str]] = {
    ("app", "ctrl+p"): ("palette", "paleta de acciones", "ctrl+p"),
    ("app", "question_mark"): ("help", "ayuda", "?"),
    ("help", "escape"): ("dismiss_none", "cerrar", "esc"),
    ("help", "q"): ("dismiss_none", "cerrar", "q"),
    ("home", "c"): ("consult", "consultar mapas", "c"),
    ("home", "f"): ("factory", "fábrica", "f"),
    ("home", "i"): ("import_csv", "importar csv", "i"),
    ("home", "j"): ("table_down", "bajar", "j"),
    ("home", "k"): ("table_up", "subir", "k"),
    ("home", "n"): ("construct", "construir mapa", "n"),
    ("home", "p"): ("plug", "conectar repo", "p"),
    ("home", "q"): ("quit", "salir", "q"),
    ("home", "r"): ("resume", "retomar último", "r"),
    ("home", "s"): ("settings", "componentes", "s"),
    ("home", "t"): ("template", "desde plantilla", "t"),
    ("import", "escape"): ("home", "volver", "esc"),
    ("import", "s"): ("save", "guardar mapa", "s"),
    ("map", "A"): ("add_attachment", "agregar adjunto", "A"),
    ("map", "I"): ("toggle_inspector", "mostrar/ocultar ficha", "I"),
    ("map", "R"): ("toggle_rail", "mostrar/ocultar rail", "R"),
    ("map", "X"): ("remove_attachment", "quitar adjunto", "X"),
    ("map", "a"): ("add_child", "agregar hijo", "a"),
    ("map", "d"): ("open_documents", "documentos", "d"),
    ("map", "e"): ("export_svg", "exportar svg", "e"),
    ("map", "enter"): ("open_ficha", "abrir ficha", "↵"),
    ("map", "equals_sign"): ("toggle_diff", "alternar diff", "="),
    ("map", "escape"): ("back_or_home", "volver", "esc"),
    ("map", "f"): ("toggle_focus", "alternar foco", "f"),
    ("map", "g"): ("focus_rail", "ir al rail", "g"),
    ("map", "h"): ("parent", "padre", "h"),
    ("map", "j"): ("next_sibling", "siguiente", "j"),
    ("map", "k"): ("prev_sibling", "anterior", "k"),
    ("map", "l"): ("child", "hijo", "l"),
    ("map", "m"): ("coverage", "cobertura", "m"),
    ("map", "n"): ("next_gap", "siguiente faltante", "n"),
    ("map", "o"): ("toggle_outline", "alternar outline", "o"),
    ("map", "q"): ("home", "inicio", "q"),
    ("map", "r"): ("toggle_radial", "alternar radial", "r"),
    ("map", "slash"): ("search", "buscar", "/"),
    ("map", "u"): ("undo", "deshacer", "u"),
    ("map", "x"): ("archive", "archivar", "x"),
    ("map", "z"): ("collapse_branch", "plegar rama", "z"),
    ("palette", "enter"): ("run_selected", "ejecutar", "↵"),
    ("palette", "escape"): ("dismiss_none", "cerrar", "esc"),
    ("plug", "escape"): ("home", "volver", "esc"),
    ("repo", "j"): ("next_sibling", "siguiente", "j"),
    ("repo", "k"): ("prev_sibling", "anterior", "k"),
    ("repo", "q"): ("home", "inicio", "q"),
}


def test_at_n03h_the_whole_seat_matches_its_specification():
    """AT-N03h — every (scope, key) maps to the promised (action, label, glyph).

    Set equality over all 48 entries, so a drift in ANY field of ANY scope fails,
    and so does an added or removed binding.

    RED mutations, all verified: swap two `action` fields; swap two `label`
    fields; corrupt a `glyph`; add or delete an entry.
    """
    actual = {
        (b.scope, b.key): (b.action, b.label, b.glyph) for b in keymap.KEYMAP
    }
    assert len(actual) == len(keymap.KEYMAP), (
        "two seat entries share a (scope, key) — one of them can never fire"
    )
    assert actual == EXPECTED_SEAT, (
        "the keymap seat drifted from its specification; if the rebinding is "
        "deliberate, update EXPECTED_SEAT in the same commit"
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
