"""Single keymap seat for the mapper UI."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class KeyBinding:
    """One mapping from a key chord to an action."""

    key: str
    action: str
    group: str


# One seat, three readers: keybar, palette, help.
KEYMAP: list[KeyBinding] = [
    # doors
    KeyBinding("c", "consult", "doors"),
    KeyBinding("p", "repo", "doors"),
    KeyBinding("n", "construct", "doors"),
    KeyBinding("t", "template", "doors"),
    KeyBinding("f", "factory", "doors"),
    # nav
    KeyBinding("j", "next", "nav"),
    KeyBinding("k", "prev", "nav"),
    KeyBinding("h", "parent", "nav"),
    KeyBinding("l", "child", "nav"),
    KeyBinding("↵", "open", "nav"),
    # node
    KeyBinding("a", "add child", "node"),
    KeyBinding("d", "document", "node"),
    KeyBinding("x", "archive", "node"),
    # view
    KeyBinding("v", "cycle view", "view"),
    KeyBinding("/", "search", "view"),
    KeyBinding("e", "export", "view"),
    # edit
    KeyBinding("tab", "preview", "edit"),
    KeyBinding("ctrl+s", "save", "edit"),
    KeyBinding("esc", "cancel", "edit"),
    # palette
    KeyBinding("j", "move down", "palette"),
    KeyBinding("k", "move up", "palette"),
    KeyBinding("↵", "run", "palette"),
    KeyBinding("esc", "close", "palette"),
    # app
    KeyBinding("ctrl+p", "palette", "app"),
    KeyBinding("?", "help", "app"),
    KeyBinding("q", "quit / home", "app"),
    KeyBinding("u", "undo", "app"),
]


def groups_for_keybar(
    active_groups: Sequence[str],
) -> list[tuple[str, list[tuple[str, str]]]]:
    """Return keybindings grouped for `darkside.keybar`.

    Each tuple is (group_name, [(key, label), ...]) in the requested order.
    """
    group_bindings: dict[str, list[tuple[str, str]]] = {}
    for binding in KEYMAP:
        if binding.group not in active_groups:
            continue
        group_bindings.setdefault(binding.group, []).append(
            (binding.key, binding.action)
        )
    return [
        (name, group_bindings.get(name, [])) for name in active_groups
    ]


def palette_items(query: str) -> list[KeyBinding]:
    """Fuzzy-filter keymap actions by key+action."""
    q = query.lower().strip()
    if not q:
        return list(KEYMAP)
    return [
        binding
        for binding in KEYMAP
        if q in (binding.key + binding.action).lower()
    ]
