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
# So the specification is the full tuple for EVERY entry (48 when this was
# written; the seat has grown twice since, and a count in this sentence would be
# stale rather than wrong-making), compared by SET
# EQUALITY. C-31 warns that a hand-listed set is usually a weak oracle; here it is
# the specification, and its whole value is that it is not derived from the thing
# it checks. A deliberate rebinding is a two-line change: the seat, and this table.
EXPECTED_SEAT: dict[tuple[str, str], tuple[str, str, str, str, bool]] = {
    ("app", "ctrl+p"): ("palette", "paleta de acciones", "ctrl+p", "app", False),
    ("app", "question_mark"): ("help", "ayuda", "?", "app", False),
    ("help", "escape"): ("dismiss_none", "cerrar", "esc", "help", False),
    ("help", "q"): ("dismiss_none", "cerrar", "q", "help", False),
    ("home", "c"): ("consult", "consultar mapas", "c", "doors", False),
    ("home", "f"): ("factory", "fábrica", "f", "doors", False),
    ("home", "i"): ("import_csv", "importar csv", "i", "doors", False),
    ("home", "j"): ("table_down", "bajar", "j", "lista", False),
    ("home", "k"): ("table_up", "subir", "k", "lista", False),
    ("home", "n"): ("construct", "construir mapa", "n", "doors", False),
    ("home", "p"): ("plug", "conectar repo", "p", "doors", False),
    ("home", "q"): ("quit", "salir", "q", "lista", False),
    ("home", "r"): ("resume", "retomar último", "r", "doors", False),
    ("home", "s"): ("settings", "componentes", "s", "doors", False),
    ("home", "t"): ("template", "desde plantilla", "t", "doors", False),
    ("import", "escape"): ("home", "volver", "esc", "import", False),
    ("import", "s"): ("save", "guardar mapa", "s", "import", False),
    ("map", "A"): ("add_attachment", "agregar adjunto", "A", "node", False),
    # Inc-3 / US-N06: the four pan chords.  `⇧hjkl` pans what `hjkl` navigates.
    ("map", "H"): ("pan_left", "desplazar izquierda", "H", "view", False),
    ("map", "I"): ("toggle_inspector", "mostrar/ocultar ficha", "I", "view", False),
    ("map", "J"): ("pan_down", "desplazar abajo", "J", "view", False),
    ("map", "K"): ("pan_up", "desplazar arriba", "K", "view", False),
    ("map", "L"): ("pan_right", "desplazar derecha", "L", "view", False),
    # Inc-4b / US-N07 `#D5b`: `n` walks the live matches, `N` walks them
    # backwards, and `next_gap` moves off `n` to `M`.
    ("map", "M"): ("next_gap", "siguiente faltante", "M", "view", False),
    ("map", "N"): ("prev_hit", "coincidencia anterior", "N", "nav", False),
    ("map", "R"): ("toggle_rail", "mostrar/ocultar rail", "R", "view", False),
    ("map", "X"): ("remove_attachment", "quitar adjunto", "X", "node", False),
    ("map", "a"): ("add_child", "agregar hijo", "a", "node", False),
    ("map", "d"): ("open_documents", "documentos", "d", "node", False),
    ("map", "e"): ("export_svg", "exportar svg", "e", "view", False),
    ("map", "enter"): ("open_ficha", "abrir ficha", "↵", "nav", False),
    ("map", "equals_sign"): ("toggle_diff", "alternar diff", "=", "view", False),
    ("map", "escape"): ("back_or_home", "volver", "esc", "salir", False),
    ("map", "f"): ("toggle_focus", "alternar foco", "f", "view", False),
    ("map", "g"): ("focus_rail", "ir al rail", "g", "view", False),
    ("map", "h"): ("parent", "padre", "h", "nav", False),
    ("map", "j"): ("next_sibling", "siguiente", "j", "nav", False),
    ("map", "k"): ("prev_sibling", "anterior", "k", "nav", False),
    ("map", "l"): ("child", "hijo", "l", "nav", False),
    ("map", "m"): ("coverage", "cobertura", "m", "view", False),
    ("map", "n"): ("next_hit", "siguiente coincidencia", "n", "nav", False),
    ("map", "o"): ("toggle_outline", "alternar outline", "o", "view", False),
    ("map", "q"): ("home", "inicio", "q", "salir", False),
    ("map", "r"): ("toggle_radial", "alternar radial", "r", "view", False),
    ("map", "slash"): ("search", "buscar", "/", "nav", False),
    ("map", "u"): ("undo", "deshacer", "u", "node", False),
    ("map", "x"): ("archive", "archivar", "x", "node", False),
    ("map", "z"): ("collapse_branch", "plegar rama", "z", "view", False),
    ("palette", "enter"): ("run_selected", "ejecutar", "↵", "palette", False),
    ("palette", "escape"): ("dismiss_none", "cerrar", "esc", "palette", False),
    ("plug", "escape"): ("home", "volver", "esc", "plug", True),
    ("repo", "j"): ("next_sibling", "siguiente", "j", "repo", True),
    ("repo", "k"): ("prev_sibling", "anterior", "k", "repo", True),
    ("repo", "q"): ("home", "inicio", "q", "repo", True),
}


def test_at_n03h_the_whole_seat_matches_its_specification():
    """AT-N03h — every (scope, key) maps to its promised tuple, all six fields.

    Set equality over all 48 entries, so a drift in ANY field of ANY scope fails,
    and so does an added or removed binding.

    `priority` is pinned too, because it is a real dispatch field: dropping
    `priority=True` from the plug-repo `escape` binding changes behaviour (the
    operator can no longer abandon the input mid-typing) and left the suite green
    while only four fields were pinned. `group` is pinned because `scope` is
    derived from it, so a regrouping silently moves a key to another surface.

    RED mutations, all verified: swap two `action` fields; swap two `label`
    fields; corrupt a `glyph`; drop a `priority`; regroup an entry; add or delete
    an entry.
    """
    actual = {
        (b.scope, b.key): (b.action, b.label, b.glyph, b.group, b.priority)
        for b in keymap.KEYMAP
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
