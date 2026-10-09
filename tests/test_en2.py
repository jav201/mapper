"""Inc-EN-2 -- census arm over the four EN-2 source files, and `Z2` (the word beside `↵` on an attachment chip).

Authority: `VERDICT-inc-en-2026-10-02.md` (EN-Q1; Round 2, `Z2`) and `VERDICT-inc8-legend-2026-09-28.md` section LANGUAGE
RULING.  The census reads each file's AST, skips docstrings and comments, and fails on any string literal that holds an
accented character or a word from SPANISH_WORDS.  The word list is explicit so a reviewer can read what the arm can and
cannot see; it does not claim to detect Spanish in general.  The `Z2` arms use real keys (`tab`) and read the painted
hint line and key bar; the OS launcher is never reached (no `enter` is pressed on a chip here).
"""
from __future__ import annotations

import ast
import pathlib
import re

import pytest

from mapper.app import MapperApp, map_hint
from mapper.model import Attachment
from mapper.widgets.chrome import HintLine, KeyBar
from tests.test_attachments import _open, _seed
from tests.test_inc9f import NARROW, SIZE
from tests.test_inc9m import _env
from tests.test_inc9x3 import _focus_chip

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILES = (
    "mapper/screens/coverage.py",
    "mapper/screens/settings.py",
    "mapper/widgets/inspector.py",
    "mapper/widgets/rail.py",
)

ACCENTED = re.compile("[áéíóúñüÁÉÍÓÚÑÜ¿¡]")

SPANISH_WORDS = frozenset("""
adjunto adjuntos agregar bloq bloque campo cargando cerrar ciclo cobertura completo componentes dibujar el estado
faltan faltantes falta ficha foco luna marea mapa nodo noche notas puede recorre requerido riesgo salir selecciona
seleccionar sistema tarde territorio todo vacio vacío
con de del el en es etiqueta la las los ningun ninguna ninguno nombre para por se sin un una y
""".split())

# `open_ficha` is the seat's action id (an identifier in `keymap.py`, not copy); `Z2` looks the seat row up by it.
ALLOW: frozenset[str] = frozenset({"open_ficha"})


def _literals(source: str):
    tree = ast.parse(source)
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str):
                docstrings.add(id(body[0].value))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
            yield node.lineno, node.value


def spanish_hits(source: str) -> list[tuple[int, str, str]]:
    hits = []
    for line, text in _literals(source):
        if text in ALLOW:
            continue
        if ACCENTED.search(text):
            hits.append((line, text, "accented character"))
            continue
        for word in re.findall(r"[^\W\d_]+", text.lower()):
            if word in SPANISH_WORDS:
                hits.append((line, text, f"word {word!r}"))
                break
    return hits


@pytest.mark.parametrize("rel", FILES)
def test_no_spanish_user_facing_string(rel):
    source = (ROOT / rel).read_text(encoding="utf-8")
    hits = spanish_hits(source)
    assert hits == [], f"{rel}: Spanish string literals: {hits}"


def test_scanner_sees_what_it_claims():
    """Oracle control: the scan flags a planted word, a planted accent and an f-string part, and passes English."""
    assert spanish_hits("x = 'todo completo.'") != []
    assert spanish_hits("x = 'salir del campo'") != []
    assert spanish_hits("x = f'mapa \u00b7 {n}n'") != []
    assert spanish_hits("x = 'ac\u00e9rcate'") != []
    assert spanish_hits("x = '(ninguna etiqueta)'") != []
    assert spanish_hits("x = 'nombre de la ruta'") != []
    assert spanish_hits("x = 'delta porter lasso unity'") == []  # whole words only: no substring hits
    assert spanish_hits("x = 'all complete.'\ny = 'no such host'") == []
    assert spanish_hits('def f():\n    """todo completo del campo"""\n') == []


# -- Z2: the word beside the enter glyph while an attachment chip has focus ------------------------------------

ENTER = "↵"
CHIPS = [
    Attachment(kind="file", path="docs/x.pdf", caption="plan"),
    Attachment(kind="url", path="https://example.com/acta", caption="acta"),
]


async def _tab_to(app, pilot, want):
    for _ in range(12):
        if getattr(app.focused, "id", None) == want:
            return
        await pilot.press("tab")
        await pilot.pause()
    raise AssertionError(f"tab never reached {want}: focus is {getattr(app.focused, 'id', None)}")


def _bar_pairs(screen):
    return [pair for _, pairs in screen.query_one(KeyBar).groups for pair in pairs]


@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_z2_a_focused_chip_says_open_attachment_on_the_hint_and_the_key_bar_and_hands_back(
        size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app, CHIPS))
        before_hint = screen.query_one(HintLine).text
        before_bar = _bar_pairs(screen)
        assert before_hint == map_hint() and (ENTER, "open card") in before_bar
        await _focus_chip(app, pilot, 0, size)
        await pilot.pause()
        hint = screen.query_one(HintLine).text
        assert f"{ENTER} open attachment" in hint and "open card" not in hint, hint
        pairs = _bar_pairs(screen)
        assert (ENTER, "open attachment") in pairs and (ENTER, "open card") not in pairs, pairs
        # chip to chip: still the attachment word, and the saved words are the originals, not our own.
        await _tab_to(app, pilot, "insp-att-1")
        assert f"{ENTER} open attachment" in screen.query_one(HintLine).text
        # off the chips: the seat's words come back, byte for byte.
        for _ in range(12):
            if not str(getattr(app.focused, "id", "") or "").startswith("insp-att-"):
                break
            await pilot.press("tab")
            await pilot.pause()
        assert not str(getattr(app.focused, "id", "") or "").startswith("insp-att-"), app.focused
        # The chip hands back what it borrowed.  If the keyboard landed on a text field,
        # that field's own hint applies (data-safety Inc-1c U2: it names `ctrl+s`).
        hint = screen.query_one(HintLine).text
        if type(app.focused).__name__ == "FieldInput":
            assert "ctrl+s save" in hint and "open attachment" not in hint, hint
        else:
            assert hint == before_hint
        assert _bar_pairs(screen) == before_bar


async def test_z2_another_field_focus_leaves_open_card_alone(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app, CHIPS))
        for _ in range(12):
            await pilot.press("tab")
            await pilot.pause()
            # Z2 scope: `open attachment` belongs to chips only.  Since data-safety Inc-1c
            # (UX-1 M2) a focused text field names `ctrl+s` instead of `open card`.
            focused = str(getattr(app.focused, "id", "") or "")
            hint = screen.query_one(HintLine).text
            if not focused.startswith("insp-att-"):
                assert "open attachment" not in hint, (app.focused, hint)
                assert f"{ENTER} open card" in hint or "ctrl+s save" in hint, (app.focused, hint)
