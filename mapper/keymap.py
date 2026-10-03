"""Single keymap seat for the mapper UI.

One declaration, four readers: screen `BINDINGS`, the keybar, the command palette
and the help overlay.  Four fields are kept deliberately separate so that the bound
name, the dispatched name and the displayed name can never be the same string by
accident (LLR-N03.1):

``key``     the Textual key name — what actually binds (``enter``, ``slash``).
``glyph``   the display form the operator reads (``↵``, ``/``).
``action``  the ``action_*`` method stem — what actually dispatches.
``label``   English prose — what the palette and help show (`A-112`).

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
# LLR-N16.1.2 / `#D9`: the last two screens that bind the help chord.
SCOPE_FACTORY = "factory"
SCOPE_SETTINGS = "settings"

# Screens whose bindings are NOT yet in this seat.  This is not decoration: it is
# the exception list the conformance tests quantify over, so a screen leaving the
# seat, or a new `tab` binding appearing on one of these, reddens a test instead of
# passing unnoticed.
UNMIGRATED_SCREENS = (
    "EditorScreen",
    "CoverageScreen",
)

# The only screens permitted to bind `tab`, and solely because they are not in the
# seat yet.  `tab` belongs to focus traversal: a screen-level `tab` binding was
# measured to produce 0 focus moves in 9 presses (LLR-N06.5).  `SettingsScreen`
# left at Inc-9: `C-D9a`'s probe, with a working positive control, measured the
# pre-drop bindings HOLDING focus on one target for all 9 presses, against 8
# transitions once they were gone.  The drop was a REPAIR, not a neutral edit
# (`tests/test_inc9.py`, `INC9-CR-F3`).
TAB_BINDING_EXCEPTIONS = ("EditorScreen",)

# Every group maps to exactly one scope.  Written down because Inc-1 generates
# `BINDINGS` from it: an undeclared group is a key nobody owns.  The order is the
# key bar's order (`bar_group_order`), and the legend paints the same order.
# `L3`: on home the doors (`open`) come BEFORE `maps`, in the bar and the legend.
GROUP_SCOPE: dict[str, str] = {
    "doors": SCOPE_HOME,
    "list": SCOPE_HOME,
    "exit": SCOPE_HOME,
    "nav": SCOPE_MAP,
    "node": SCOPE_MAP,
    "view": SCOPE_MAP,
    "leave": SCOPE_MAP,
    "repo": SCOPE_REPO,
    "plug": SCOPE_PLUG,
    "import": SCOPE_IMPORT,
    # Before `app`: `keybar_groups` paints a scope's groups in THIS order, and
    # the app-wide group closes every bar (`INC9-F6`, seen in the renders).
    "tree": SCOPE_FACTORY,
    "document": SCOPE_FACTORY,
    "factory": SCOPE_FACTORY,
    "settings": SCOPE_SETTINGS,
    "palette": SCOPE_PALETTE,
    "help": SCOPE_HELP,
    "app": SCOPE_APP,
}

# What each group is CALLED where the operator reads it: the key bar, the legend
# and the palette (`K1`, `K4`).  The group id above is the seat's own handle and
# names exactly one scope; the header is prose and two scopes may share one word
# (`nav` on the map and `tree` in the factory are both `move`).
GROUP_HEADER: dict[str, str] = {
    "list": "maps",
    "doors": "open",
    "exit": "exit",
    "nav": "move",
    "node": "node",
    "view": "view",
    "leave": "leave",
    "repo": "repo",
    "plug": "connect repo",
    "import": "import",
    "tree": "move",
    "document": "document",
    "factory": "factory",
    "settings": "components",
    "palette": "palette",
    "help": "help",
    "app": "global",
}


def group_header(group: str) -> str:
    """The header painted for *group* (key bar, legend, palette)."""
    return GROUP_HEADER[group]


def bar_group_order(scope: str) -> list[str]:
    """The group ids a *scope* paints, in the key bar's order: the scope's own
    groups in `GROUP_SCOPE` order, then the app-wide group that closes every bar.
    The legend reads this too (`INC9-UX-F10`), so the two cannot disagree."""
    return [g for g, s in GROUP_SCOPE.items() if s in (scope, SCOPE_APP)]


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
    KeyBinding("c", "c", "consult", "browse maps", "doors"),
    KeyBinding("p", "p", "plug", "connect repo", "doors"),
    KeyBinding("n", "n", "construct", "build map", "doors"),
    KeyBinding("t", "t", "template", "from template", "doors"),
    KeyBinding("i", "i", "import_csv", "import csv", "doors"),
    KeyBinding("f", "f", "factory", "factory", "doors"),
    KeyBinding("r", "r", "resume", "resume last", "doors"),
    KeyBinding("s", "s", "settings", "components", "doors"),
    KeyBinding("j", "j", "table_down", "next map", "list"),
    KeyBinding("k", "k", "table_up", "previous map", "list"),
    # `INC9-UX-F11`: the home key bar has always said `↵ open`; the recents table
    # answers it only while it holds focus, so the seat declares it and the
    # screen answers it from anywhere on the screen.
    KeyBinding("enter", "↵", "open_selected", "open map", "list"),
    # Not a list action: it leaves the application.
    KeyBinding("q", "q", "quit", "quit", "exit"),
    # -- map · navigation ---------------------------------------------------
    KeyBinding("j", "j", "next_sibling", "next sibling", "nav"),
    KeyBinding("k", "k", "prev_sibling", "previous sibling", "nav"),
    KeyBinding("h", "h", "parent", "parent", "nav"),
    KeyBinding("l", "l", "child", "child", "nav"),
    KeyBinding("enter", "↵", "open_ficha", "open card", "nav"),
    KeyBinding("slash", "/", "search", "search", "nav"),
    # US-N07 `#D5b`.  `n` walks the live *coincidencias* set and `N` walks it
    # backwards, in `nav` beside the `/` that produces the set.  `n` used to be
    # `next_gap`, which moves to `M` in the `view` block below: the walk is the
    # chord an operator reaches for several times per search, the coverage
    # worklist is reached for once, and only one of the two can own the letter
    # its Spanish label starts with.  Both labels are true in EVERY state, so the
    # seat stays a static set and the whole-seat pin stays set equality (`#D10`).
    KeyBinding("n", "n", "next_hit", "next match", "nav"),
    KeyBinding("N", "N", "prev_hit", "previous match", "nav"),
    # -- map · node ---------------------------------------------------------
    KeyBinding("a", "a", "add_child", "add child", "node"),
    KeyBinding("d", "d", "open_documents", "documents", "node"),
    KeyBinding("x", "x", "archive", "archive node", "node"),
    KeyBinding("u", "u", "undo", "undo", "node"),
    KeyBinding("A", "A", "add_attachment", "add attachment", "node"),
    KeyBinding("X", "X", "remove_attachment", "remove attachment", "node"),
    # -- map · view ---------------------------------------------------------
    KeyBinding("f", "f", "toggle_focus", "focus branch", "view"),
    KeyBinding("o", "o", "toggle_outline", "toggle outline", "view"),
    KeyBinding("r", "r", "toggle_radial", "toggle mind map", "view"),
    KeyBinding("e", "e", "export_svg", "export svg", "view"),
    KeyBinding("equals_sign", "=", "toggle_diff", "show/hide diff", "view"),
    KeyBinding("m", "m", "coverage", "coverage report", "view"),
    # Relocated from `n` by `#D5b`.  Uppercase because the shifted-pair
    # precedent is already in this seat (`A`/`X` beside `a`/`x`, `HJKL` beside
    # `hjkl`) and `M` was free: of the uppercase letters only `A`, `H`, `I`,
    # `J`, `K`, `L`, `R` and `X` were taken before this row.
    KeyBinding("M", "M", "next_gap", "next incomplete", "view"),
    KeyBinding("R", "R", "toggle_rail", "show/hide rail", "view"),
    KeyBinding("I", "I", "toggle_inspector", "show/hide card", "view"),
    KeyBinding("g", "g", "focus_rail", "go to rail", "view"),
    KeyBinding("z", "z", "collapse_branch", "fold/unfold", "view"),
    # US-N06 pan.  `hjkl` already navigates the tree in this scope and `⇧hjkl`
    # moves the window over it — the shifted-pair precedent is already in the
    # seat (`A`/`X` beside `a`/`x`).  Executed at `ea1fbf9` and re-derived at
    # `954f8f3`: all four arrive as their own `event.key`, and of the uppercase
    # letters only `A`, `I`, `R` and `X` were taken.
    KeyBinding("H", "H", "pan_left", "pan left", "view"),
    KeyBinding("J", "J", "pan_down", "pan down", "view"),
    KeyBinding("K", "K", "pan_up", "pan up", "view"),
    KeyBinding("L", "L", "pan_right", "pan right", "view"),
    # -- map · leaving ------------------------------------------------------
    KeyBinding("q", "q", "home", "home", "leave"),
    KeyBinding("escape", "esc", "back_or_home", "back", "leave"),
    # -- repo ---------------------------------------------------------------
    KeyBinding("j", "j", "next_sibling", "next branch", "repo", priority=True),
    KeyBinding("k", "k", "prev_sibling", "previous branch", "repo", priority=True),
    # It lands on the connect-repo screen, not home.
    KeyBinding("q", "q", "home", "back", "repo", priority=True),
    # -- plug repo ----------------------------------------------------------
    # `escape` stays priority here: the screen's only widget is a text input the
    # operator must be able to abandon mid-typing.
    KeyBinding("escape", "esc", "home", "back", "plug", priority=True),
    # -- import preview -----------------------------------------------------
    KeyBinding("s", "s", "save", "save map", "import"),
    KeyBinding("escape", "esc", "home", "back", "import"),
    # -- palette (modal) ----------------------------------------------------
    # The footer reads these two as one `↑↓ move` pair.  Both rows carry the one
    # word, so the pair never reads two ways.
    KeyBinding("up", "↑", "move_up", "move", "palette"),
    KeyBinding("down", "↓", "move_down", "move", "palette"),
    KeyBinding("enter", "↵", "run_selected", "run", "palette"),
    KeyBinding("escape", "esc", "dismiss_none", "close", "palette"),
    # -- help (modal) -------------------------------------------------------
    # Its own scope: borrowing the palette's bound `enter -> run_selected`, a
    # method HelpScreen does not define, which was a silent no-op.
    KeyBinding("escape", "esc", "dismiss_none", "close", "help"),
    KeyBinding("q", "q", "dismiss_none", "close", "help"),
    # HLR-N16.4: every key that has an effect inside the legend is declared in
    # it.  These six already scrolled the pane, undeclared, while the new
    # vocabulary sections land below the fold.
    KeyBinding("up", "↑", "legend_up", "scroll up", "help"),
    KeyBinding("down", "↓", "legend_down", "scroll down", "help"),
    KeyBinding("pageup", "pageup", "legend_page_up", "page up", "help"),
    KeyBinding("pagedown", "pagedown", "legend_page_down", "page down", "help"),
    KeyBinding("home", "home", "legend_home", "to top", "help"),
    KeyBinding("end", "end", "legend_end", "to bottom", "help"),
    # -- factory (LLR-N16.1.2, `#D9`) ----------------------------------------
    # Migrated from the screen's own list with `priority` kept: every one of
    # its bindings was `priority=True`, and the migration changes no dispatch.
    KeyBinding("j", "j", "next_sibling", "next sibling", "tree", priority=True),
    KeyBinding("k", "k", "prev_sibling", "previous sibling", "tree", priority=True),
    KeyBinding("h", "h", "parent", "parent", "tree", priority=True),
    KeyBinding("l", "l", "child", "child", "tree", priority=True),
    KeyBinding("0", "0", "start_node", "back to start", "tree", priority=True),
    KeyBinding("d", "d", "edit_doc", "edit document", "document", priority=True),
    KeyBinding("i", "i", "import_office", "import office file", "document", priority=True),
    KeyBinding("g", "g", "generate_office", "generate office file", "document", priority=True),
    KeyBinding("q", "q", "home", "back", "factory", priority=True),
    KeyBinding("escape", "esc", "home", "back", "factory", priority=True),
    # -- settings (LLR-N16.1.2, `#D9`) ---------------------------------------
    # No `tab`/`shift+tab` rows: the screen only re-declared Textual's own
    # traversal, and `C-D9a` measured dropping them neutral.
    KeyBinding("q", "q", "home", "back", "settings", priority=True),
    KeyBinding("escape", "esc", "home", "back", "settings", priority=True),
    # -- app (available on every screen) ------------------------------------
    KeyBinding("ctrl+p", "ctrl+p", "palette", "palette", "app"),
    # Not priority, on purpose (`T3`, `EN-Q3`): a focused `Input` consumes `?` before a
    # non-priority binding is asked, so `?` types in every text field and opens the
    # legend everywhere else.  A priority row would take the key from the field.
    KeyBinding("question_mark", "?", "help", "legend", "app"),
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

    Each tuple is (header, [(glyph, label), ...]) in the requested order, the
    header being what the operator reads (`group_header`), not the group id.
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
    return [(group_header(name), group_bindings.get(name, [])) for name in active_groups]


def hint_pair(scope: str, action: str, key: str | None = None) -> str:
    """`"glyph label"` of the ONE seat row *scope* binds to *action* (narrowed by
    *key* when an action has two chords, as `home` does in the factory).

    Key hints painted outside the key bar -- a screen's hint line, a modal's
    footer -- are built from this, so the word beside a key is the seat's word
    (`K3`): the same key never reads two ways on one screen.
    """
    rows = [
        b for b in KEYMAP
        if b.scope == scope and b.action == action and (key is None or b.key == key)
    ]
    if len(rows) != 1:
        raise KeyError((scope, action, key, len(rows)))
    return f"{rows[0].glyph} {rows[0].label}"


def label_for(scope: str, action: str) -> str:
    """The label of the one seat row *scope* binds to *action*."""
    return hint_pair(scope, action).split(" ", 1)[1]


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
