"""Inc-EN-3 -- census arm over the four EN-3 source files (the views).

Authority: `VERDICT-inc-en-2026-10-02.md` (EN-Q1) and `VERDICT-inc8-legend-2026-09-28.md` section LANGUAGE RULING.
Same method as `test_en2.py`: the arm reads each file's AST, skips docstrings and comments, and fails on any string
literal that holds an accented character or a word from SPANISH_WORDS (whole words, never substrings).  The list is
explicit so a reviewer can read what the arm can and cannot see; it does not claim to detect Spanish in general.
"""
from __future__ import annotations

import ast
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILES = (
    "mapper/views/lane.py",
    "mapper/views/layered.py",
    "mapper/views/outline.py",
    "mapper/views/radial.py",
)

ACCENTED = re.compile("[áéíóúñüÁÉÍÓÚÑÜ¿¡]")

SPANISH_WORDS = frozenset("""
acta actas arbol aristas completo conteos cobertura dibujo eliminados etiquetas fichas fuera limite listado mapa
nodo nodos omitio rama ramas supera vista
con de del el en es etiqueta la las los ningun ninguna ninguno nombre para por se sin un una y
""".split())


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
    assert spanish_hits("x = '(sin ramas)'") != []
    assert spanish_hits("x = ' fuera de vista'") != []
    assert spanish_hits("x = '▫ sin acta'") != []
    assert spanish_hits("x = f'mapa de {n} nodos'") != []
    assert spanish_hits("x = 'límite'") != []
    assert spanish_hits("x = '(ninguna etiqueta)'") != []
    assert spanish_hits("x = 'delta porter lasso unity'") == []  # whole words only: no substring hits
    assert spanish_hits("x = '(no branches)'\ny = ' out of view'\nz = '▫ no record'") == []
    assert spanish_hits('def f():\n    """sin ramas del mapa"""\n') == []


def test_hybrid_lane_with_no_branches_says_so_in_english():
    """The one lane string the census list names; read from the painted text, not only from the AST."""
    from mapper.model import Ficha, Graph, Node
    from mapper.views.lane import HybridLaneRenderer
    from mapper.views.state import ViewState

    graph = Graph()
    graph.add_node(Node(id="repo", ficha=Ficha(title="repo")))
    graph.root_id = "repo"
    text = HybridLaneRenderer().render(graph, ViewState(w=118, h=34)).plain
    assert "(no branches)" in text, text
