"""Single keymap seat for the mapper UI.

One declaration, four readers: screen `BINDINGS`, the keybar, the command palette
and the help overlay.  Four fields are kept deliberately separate so that the bound
name, the dispatched name and the displayed name can never be the same string by
accident (LLR-N03.1):

``key``     the Textual key name — what actually binds (``enter``, ``slash``).
``glyph``   the display form the operator reads (``↵``, ``/``).
``action``  the ``action_*`` method stem — what actually dispatches.
``label``   Spanish prose — what the palette and help show.

This module has no Textual dependency: it returns plain tuples and the screen turns
them into ``Binding`` objects.  The dependency ban in ``docs/ARCHITECTURE.md`` §3
is what keeps it that way.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

# Scopes ------------------------------------------------------------------
# A scope is "which surface owns this key".  The same chord may appear in two
# scopes (``q`` quits from home and returns home from a map); it may never appear
# twice inside one scope (LLR-N03.6).
SCOPE_HOME = "home"
SCOPE_MAP = "map"
SCOPE_REPO = "repo"
SCOPE_PLUG = "plug"
SCOPE_IMPORT = "import"
SCOPE_PALETTE = "palette"
SCOPE_HELP = "help"
SCOPE_APP = "app"

# Screens whose bindings are NOT yet in this seat.  This is not decoration: it is
# the exception list the conformance tests quantify over, so a screen leaving the
# seat, or a new `tab` binding appearing on one of these, reddens a test instead of
# passing unnoticed.
UNMIGRATED_SCREENS = (
    "FactoryScreen",
    "EditorScreen",
    "SettingsScreen",
    "CoverageScreen",
)

# The only screens permitted to bind `tab`, and solely because they are not in the
# seat yet.  `tab` belongs to focus traversal: a screen-level `tab` binding was
# measured to produce 0 focus moves in 9 presses (LLR-N06.5).
TAB_BINDING_EXCEPTIONS = ("SettingsScreen", "EditorScreen")

# Every group maps to exactly one scope.  Written down because Inc-1 generates
# `BINDINGS` from it: an undeclared group is a key nobody owns.
GROUP_SCOPE: dict[str, str] = {
    "doors": SCOPE_HOME,
    "lista": SCOPE_HOME,
    "nav": SCOPE_MAP,
    "node": SCOPE_MAP,
    "view": SCOPE_MAP,
    "salir": SCOPE_MAP,
    "repo": SCOPE_REPO,
    "plug": SCOPE_PLUG,
    "import": SCOPE_IMPORT,
    "palette": SCOPE_PALETTE,
    "help": SCOPE_HELP,
    "app": SCOPE_APP,
}


@dataclass(frozen=True, slots=True)
class KeyBinding:
    """One mapping from a key chord to an action that really exists."""

    key: str
    glyph: str
    action: str
    label: str
    group: str
    priority: bool = False

    @property
    def scope(self) -> str:
        return GROUP_SCOPE[self.group]


# The seat.  Every `action` here is an `action_*` method on the screen that owns
# the binding's scope — asserted at import time by tests/test_keymap.py.
KEYMAP: list[KeyBinding] = [
    # -- home ---------------------------------------------------------------
    KeyBinding("c", "c", "consult", "consultar mapas", "doors"),
    KeyBinding("p", "p", "plug", "conectar repo", "doors"),
    KeyBinding("n", "n", "construct", "construir mapa", "doors"),
    KeyBinding("t", "t", "template", "desde plantilla", "doors"),
    KeyBinding("i", "i", "import_csv", "importar csv", "doors"),
    KeyBinding("f", "f", "factory", "fábrica", "doors"),
    KeyBinding("r", "r", "resume", "retomar último", "doors"),
    KeyBinding("s", "s", "settings", "componentes", "doors"),
    KeyBinding("j", "j", "table_down", "bajar", "lista"),
    KeyBinding("k", "k", "table_up", "subir", "lista"),
    KeyBinding("q", "q", "quit", "salir", "lista"),
    # -- map · navigation ---------------------------------------------------
    KeyBinding("j", "j", "next_sibling", "siguiente", "nav"),
    KeyBinding("k", "k", "prev_sibling", "anterior", "nav"),
    KeyBinding("h", "h", "parent", "padre", "nav"),
    KeyBinding("l", "l", "child", "hijo", "nav"),
    KeyBinding("enter", "↵", "open_ficha", "abrir ficha", "nav"),
    KeyBinding("slash", "/", "search", "buscar", "nav"),
    # US-N07 `#D5b`.  `n` walks the live *coincidencias* set and `N` walks it
    # backwards, in `nav` beside the `/` that produces the set.  `n` used to be
    # `next_gap`, which moves to `M` in the `view` block below: the walk is the
    # chord an operator reaches for several times per search, the coverage
    # worklist is reached for once, and only one of the two can own the letter
    # its Spanish label starts with.  Both labels are true in EVERY state, so the
    # seat stays a static set and the whole-seat pin stays set equality (`#D10`).
    KeyBinding("n", "n", "next_hit", "siguiente coincidencia", "nav"),
    KeyBinding("N", "N", "prev_hit", "coincidencia anterior", "nav"),
    # -- map · node ---------------------------------------------------------
    KeyBinding("a", "a", "add_child", "agregar hijo", "node"),
    KeyBinding("d", "d", "open_documents", "documentos", "node"),
    KeyBinding("x", "x", "archive", "archivar", "node"),
    KeyBinding("u", "u", "undo", "deshacer", "node"),
    KeyBinding("A", "A", "add_attachment", "agregar adjunto", "node"),
    KeyBinding("X", "X", "remove_attachment", "quitar adjunto", "node"),
    # -- map · view ---------------------------------------------------------
    KeyBinding("f", "f", "toggle_focus", "alternar foco", "view"),
    KeyBinding("o", "o", "toggle_outline", "alternar outline", "view"),
    KeyBinding("r", "r", "toggle_radial", "alternar radial", "view"),
    KeyBinding("e", "e", "export_svg", "exportar svg", "view"),
    KeyBinding("equals_sign", "=", "toggle_diff", "alternar diff", "view"),
    KeyBinding("m", "m", "coverage", "cobertura", "view"),
    # Relocated from `n` by `#D5b`.  Uppercase because the shifted-pair
    # precedent is already in this seat (`A`/`X` beside `a`/`x`, `HJKL` beside
    # `hjkl`) and `M` was free: of the uppercase letters only `A`, `H`, `I`,
    # `J`, `K`, `L`, `R` and `X` were taken before this row.
    KeyBinding("M", "M", "next_gap", "siguiente faltante", "view"),
    KeyBinding("R", "R", "toggle_rail", "mostrar/ocultar rail", "view"),
    KeyBinding("I", "I", "toggle_inspector", "mostrar/ocultar ficha", "view"),
    KeyBinding("g", "g", "focus_rail", "ir al rail", "view"),
    KeyBinding("z", "z", "collapse_branch", "plegar rama", "view"),
    # US-N06 pan.  `hjkl` already navigates the tree in this scope and `⇧hjkl`
    # moves the window over it — the shifted-pair precedent is already in the
    # seat (`A`/`X` beside `a`/`x`).  Executed at `ea1fbf9` and re-derived at
    # `954f8f3`: all four arrive as their own `event.key`, and of the uppercase
    # letters only `A`, `I`, `R` and `X` were taken.
    KeyBinding("H", "H", "pan_left", "desplazar izquierda", "view"),
    KeyBinding("J", "J", "pan_down", "desplazar abajo", "view"),
    KeyBinding("K", "K", "pan_up", "desplazar arriba", "view"),
    KeyBinding("L", "L", "pan_right", "desplazar derecha", "view"),
    # -- map · leaving ------------------------------------------------------
    KeyBinding("q", "q", "home", "inicio", "salir"),
    KeyBinding("escape", "esc", "back_or_home", "volver", "salir"),
    # -- repo ---------------------------------------------------------------
    KeyBinding("j", "j", "next_sibling", "siguiente", "repo", priority=True),
    KeyBinding("k", "k", "prev_sibling", "anterior", "repo", priority=True),
    KeyBinding("q", "q", "home", "inicio", "repo", priority=True),
    # -- plug repo ----------------------------------------------------------
    # `escape` stays priority here: the screen's only widget is a text input the
    # operator must be able to abandon mid-typing.
    KeyBinding("escape", "esc", "home", "volver", "plug", priority=True),
    # -- import preview -----------------------------------------------------
    KeyBinding("s", "s", "save", "guardar mapa", "import"),
    KeyBinding("escape", "esc", "home", "volver", "import"),
    # -- palette (modal) ----------------------------------------------------
    KeyBinding("enter", "↵", "run_selected", "ejecutar", "palette"),
    KeyBinding("escape", "esc", "dismiss_none", "cerrar", "palette"),
    # -- help (modal) -------------------------------------------------------
    # Its own scope: borrowing the palette's bound `enter -> run_selected`, a
    # method HelpScreen does not define, which was a silent no-op.
    KeyBinding("escape", "esc", "dismiss_none", "cerrar", "help"),
    KeyBinding("q", "q", "dismiss_none", "cerrar", "help"),
    # -- app (available on every screen) ------------------------------------
    KeyBinding("ctrl+p", "ctrl+p", "palette", "paleta de acciones", "app"),
    KeyBinding("question_mark", "?", "help", "ayuda", "app"),
]


# Modal scopes do NOT inherit the app-wide chords: a modal that rebound `ctrl+p`
# would reopen the palette on top of itself.  Declared here, in the seat, so the
# screens and the tests read one source instead of each passing a flag.
MODAL_SCOPES = (SCOPE_PALETTE, SCOPE_HELP)


def bindings_for(scope: str, *, include_app: bool | None = None) -> list[KeyBinding]:
    """Every binding the given scope offers.

    App-scope bindings are reachable from every ordinary screen, so they are
    included — that is what makes "help shows exactly the keys that work here"
    true rather than aspirational.  Modal scopes are the exception.
    """
    if include_app is None:
        include_app = scope not in MODAL_SCOPES
    wanted = {scope}
    if include_app and scope != SCOPE_APP:
        wanted.add(SCOPE_APP)
    return [b for b in KEYMAP if b.scope in wanted]


def textual_bindings(
    scope: str, *, include_app: bool | None = None
) -> list[tuple[str, str, str, bool]]:
    """`(key, action, label, priority)` tuples for a screen's `BINDINGS`.

    Returned as plain tuples so this module stays free of Textual; the screen
    converts them into `Binding` objects.
    """
    return [
        (b.key, b.action, b.label, b.priority)
        for b in bindings_for(scope, include_app=include_app)
    ]


def groups_for_keybar(
    active_groups: Sequence[str],
) -> list[tuple[str, list[tuple[str, str]]]]:
    """Return keybindings grouped for `darkside.keybar`.

    Each tuple is (group_name, [(glyph, label), ...]) in the requested order.
    The keybar shows the *glyph*, never the Textual key name — nobody presses a
    key called "question_mark".
    """
    group_bindings: dict[str, list[tuple[str, str]]] = {}
    for binding in KEYMAP:
        if binding.group not in active_groups:
            continue
        group_bindings.setdefault(binding.group, []).append(
            (binding.glyph, binding.label)
        )
    return [(name, group_bindings.get(name, [])) for name in active_groups]


def palette_items(query: str, scope: str = SCOPE_APP) -> list[KeyBinding]:
    """Fuzzy-filter the bindings reachable from *scope* by glyph, label and action."""
    candidates = bindings_for(scope)
    q = query.lower().strip()
    if not q:
        return candidates
    return [
        binding
        for binding in candidates
        if q in (binding.glyph + binding.label + binding.action).lower()
    ]


def duplicate_chords() -> list[tuple[str, str]]:
    """Return `(scope, key)` pairs bound more than once inside one scope.

    A duplicate inside a single scope is a real collision: only one of the two
    actions can ever fire, and which one is an accident of list order.  Across
    scopes it is legitimate — `q` leaves a map and quits from home.
    """
    seen: set[tuple[str, str]] = set()
    clashes: list[tuple[str, str]] = []
    for binding in KEYMAP:
        pair = (binding.scope, binding.key)
        if pair in seen:
            clashes.append(pair)
        seen.add(pair)
    # An app-scope chord is reachable from every screen, so it also clashes with
    # any same-key binding in a concrete scope.
    app_keys = {b.key for b in KEYMAP if b.scope == SCOPE_APP}
    for binding in KEYMAP:
        if binding.scope != SCOPE_APP and binding.key in app_keys:
            clashes.append((binding.scope, binding.key))
    return sorted(set(clashes))
