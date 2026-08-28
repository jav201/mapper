"""Tests for SVG export."""
import unicodedata
from pathlib import Path

from mapper import darkside
from mapper.export import save_svg
from mapper.model import Edge, Ficha, Graph, Node
from mapper.views.layered import LayeredRenderer
from mapper.views.radial import RadialRenderer

BRAILLE = range(0x2800, 0x2900)


def _disk_braille(path: Path) -> int:
    """Scan CODE POINTS in the written bytes.

    Not a substring search for a rendered run: `radial.py` assigns a per-branch
    tint to every dot, so Rich emits one <text> span per style run and a
    12-glyph run is recoverable as a substring only under a UNIFORM style.
    Measured -- uniform style: 5 <text> nodes, substring True; the real 3-tone
    scheme: 16 <text> nodes, substring False, longest recoverable run 1 of 12.
    An implementer who writes the positive control the easy way measures the
    first and concludes the caveat was wrong.
    """
    raw = path.read_text(encoding="utf-8")
    return sum(1 for c in raw if ord(c) in BRAILLE)


def _screen_braille(text) -> int:
    return sum(1 for c in text.plain if ord(c) in BRAILLE)


def _radial_graph() -> Graph:
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="mapa")))
    for i, title in enumerate(("finanzas", "inventarios", "nomina", "compras")):
        g.add_node(Node(id=f"n{i}", ficha=Ficha(title=title)))
        g.add_edge(Edge("root", f"n{i}"))
    return g


def test_save_svg(tmp_path):
    g = Graph()
    g.add_node(Node(id="a", ficha=Ficha(title="A ◆ unicode")))
    text = LayeredRenderer().render(g, selected_id="a", w=40, h=12)
    out = tmp_path / "out.svg"
    save_svg(text, out)
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "<svg" in content
    assert "A" in content


def test_at_009_the_exported_file_carries_the_canvas_layers(tmp_path):
    """The assertion is ON THE WRITTEN FILE, and `size > 0` is not the threshold.

    Executed at d877784, the real chain RadialRenderer -> save_svg -> disk:
    the PRE-STATE wrote a 19 679-byte SVG containing ZERO braille, and the
    shipped `size > 0` passed on it; a payload-free export wrote 2 732 bytes
    with zero braille, and `size > 0` passed again.  It passes on an artifact
    containing zero braille, twice.  That is the vacuity, shown rather than
    argued -- so the threshold is an on-disk code-point count compared against
    the on-screen count, both computed at run time.
    """
    text = RadialRenderer().render(_radial_graph(), selected_id=None, w=80, h=24)
    out = tmp_path / "radial.svg"
    save_svg(text, out)

    assert out.exists() and out.stat().st_size > 0     # preconditions, NOT the threshold
    on_screen = _screen_braille(text)
    assert on_screen > 0, "the arm must run on a render that actually emits braille"
    assert _disk_braille(out) == on_screen


def test_at_009_the_negative_control_shows_size_alone_proves_nothing(tmp_path):
    """A payload-free export: non-empty file, zero braille, `size > 0` green.

    This is what makes the count above admissible as evidence rather than a
    number that happens to agree (C-55): the oracle can produce a non-absence,
    and it can produce an absence, and they differ.
    """
    text = LayeredRenderer().render(_radial_graph(), selected_id=None, w=80, h=24)
    out = tmp_path / "layered.svg"
    save_svg(text, out)

    assert out.stat().st_size > 0
    assert _screen_braille(text) == 0
    assert _disk_braille(out) == 0


def test_at_009_the_exported_svg_carries_no_coerced_code_point(tmp_path):
    """An SVG LEAVES THE MACHINE; the terminal's escaping does not travel with it.

    The file is opened later by a browser or an editor with entirely different
    rules, which is why this is not covered by the on-screen coercion
    thresholds.  The hostile title is CONSTRUCTED here, never spelled.
    """
    hostile = (
        "acta" + chr(0x202E) + "gpj.evil" + chr(0x202C) + chr(0x0007) + chr(0x200B)
        + chr(0x00AD) + chr(0x2062) + chr(0x206C) + chr(0xE0041) + chr(0xE0001)
    )
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title=hostile)))
    g.add_node(Node(id="b", ficha=Ficha(title="hijo" + chr(0x2028) + "x")))
    g.add_edge(Edge("root", "b"))

    text = RadialRenderer().render(g, selected_id=None, w=80, h=24)
    out = tmp_path / "hostile.svg"
    save_svg(text, out)
    raw = out.read_text(encoding="utf-8")

    # THE ORACLE IS UNICODE, NOT `COERCION_RANGES`.
    #
    # Deriving the banned set from the same constant `_CONTROL_MAP` is derived
    # from makes this assertion true for ANY value of that constant, provided
    # the coercion runs at all.  It would prove that radial calls `plain()` --
    # a routing test -- while staying green under an under-inclusive list, which
    # is precisely how the C0 row's missing carriage return survived being read.
    # Measured: under the constant-derived oracle this file reported green while
    # 19 invisible code points, the U+E0020 TAG block among them, reached this
    # same artifact.
    survivors = sorted({
        ord(c) for c in raw
        if unicodedata.category(c) in ("Cc", "Cf", "Zl", "Zp")
        and ord(c) not in darkside.PRESERVED_CODE_POINTS
    })
    assert survivors == [], (
        "invisible or control code points reached the SVG: "
        f"{[f'U+{c:04X}' for c in survivors]}"
    )

    # Positive control: the same unmodified oracle must be able to report a
    # NON-absence, or the empty result above is not evidence of anything.
    planted = raw + chr(0x2062) + chr(0xE0041)
    assert len({
        ord(c) for c in planted
        if unicodedata.category(c) in ("Cc", "Cf", "Zl", "Zp")
        and ord(c) not in darkside.PRESERVED_CODE_POINTS
    }) == 2
