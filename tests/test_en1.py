"""Inc-EN-1 -- census arm: no Spanish in a user-facing string of the four EN-1 source files.

Authority: `VERDICT-inc-en-2026-10-02.md` (EN-Q1) and `VERDICT-inc8-legend-2026-09-28.md` section LANGUAGE RULING
(every UI string is English).  The scan reads each file's AST, skips docstrings and comments, and fails on any
string literal that holds an accented character or a word from SPANISH_WORDS.  ALLOW holds the literals that are
not UI copy (English matchers for git output, none of which is Spanish).  The word list is explicit so a
reviewer can read what the arm can and cannot see; it does not claim to detect Spanish in general.
"""
from __future__ import annotations

import ast
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILES = (
    "mapper/osopen.py",
    "mapper/github.py",
    "mapper/screens/factory.py",
    "mapper/screens/editor.py",
)

ACCENTED = re.compile("[áéíóúñüÁÉÍÓÚÑÜ¿¡]")

SPANISH_WORDS = frozenset("""
abierto abrible abrir archivo calculando cancelar ciclo con del destino detectados dibujar documento el esquema
espacio fuera generado generar guardar importada importar inválido leyendo listo mapa ninguno no‑se
permitido plantilla prever proceso pudo ramas ruta salvar se sin solo tipo trabajo válido vacío
""".split())

ALLOW: frozenset[str] = frozenset()


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
    assert spanish_hits("x = 'archivo no encontrado'") != []
    assert spanish_hits("x = 'destino inv\u00e1lido'") != []
    assert spanish_hits("x = f'generado: {y}'") != []
    assert spanish_hits("x = 'file not found'\ny = 'no such host'") == []
    assert spanish_hits('def f():\n    """archivo sin documento"""\n') == []
