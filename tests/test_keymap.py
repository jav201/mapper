"""Tests for the single keymap seat."""
from mapper.keymap import KEYMAP, groups_for_keybar, palette_items


def test_keymap_has_door_bindings():
    keys = {b.key for b in KEYMAP}
    assert {"c", "p", "n", "f"}.issubset(keys)


def test_groups_for_keybar_order():
    groups = groups_for_keybar(["nav", "app"])
    names = [g[0] for g in groups]
    assert names == ["nav", "app"]
    nav_pairs = groups[0][1]
    assert any(k == "j" and a == "next" for k, a in nav_pairs)


def test_palette_items_fuzzy_filter():
    items = palette_items("pal")
    assert any("palette" in b.action for b in items)


def test_palette_items_empty_query_returns_all():
    items = palette_items("")
    assert len(items) == len(KEYMAP)
