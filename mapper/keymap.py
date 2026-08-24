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
    KeyBinding("c", "consultar", "doors"),
    KeyBinding("p", "repo", "doors"),
    KeyBinding("n", "construir", "doors"),
    KeyBinding("t", "plantilla", "doors"),
    KeyBinding("i", "importar csv", "doors"),
    KeyBinding("f", "fábrica", "doors"),
    # nav
    KeyBinding("j", "siguiente", "nav"),
    KeyBinding("k", "anterior", "nav"),
    KeyBinding("h", "padre", "nav"),
    KeyBinding("l", "hijo", "nav"),
    KeyBinding("↵", "abrir", "nav"),
    # node
    KeyBinding("a", "agregar hijo", "node"),
    KeyBinding("d", "documento", "node"),
    KeyBinding("x", "archivar", "node"),
    # view
    KeyBinding("f", "alternar foco", "view"),
    KeyBinding("o", "alternar outline", "view"),
    KeyBinding("r", "alternar radial", "view"),
    KeyBinding("v", "cambiar vista", "view"),
    KeyBinding("/", "buscar", "view"),
    KeyBinding("e", "exportar", "view"),
    KeyBinding("=", "alternar diff", "view"),
    KeyBinding("m", "cobertura", "view"),
    # edit
    KeyBinding("tab", "vista previa", "edit"),
    KeyBinding("ctrl+s", "guardar", "edit"),
    KeyBinding("esc", "cancelar", "edit"),
    # palette
    KeyBinding("j", "bajar", "palette"),
    KeyBinding("k", "subir", "palette"),
    KeyBinding("↵", "ejecutar", "palette"),
    KeyBinding("esc", "cerrar", "palette"),
    # app
    KeyBinding("ctrl+p", "paleta", "app"),
    KeyBinding("?", "ayuda", "app"),
    KeyBinding("q", "salir / inicio", "app"),
    KeyBinding("u", "deshacer", "app"),
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
