"""Inc-EN-5 -- census arm over `app.py`, plus arms for the security-bearing toasts and the search constants.

Authority: `VERDICT-inc-en-2026-10-02.md` (EN-Q1, EN-Q2) and `VERDICT-inc8-legend-2026-09-28.md` section LANGUAGE RULING.
Same method as `test_en2.py` .. `test_en4.py`: the arm reads the AST, skips docstrings and comments, and fails on any
string literal that holds an accented character or a word from SPANISH_WORDS (whole words, never substrings).  The
list is explicit so a reviewer can read what the arm can and cannot see; it does not claim to detect Spanish in general.
"""
from __future__ import annotations

import ast
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILES = ("mapper/app.py",)

ACCENTED = re.compile("[áéíóúñüÁÉÍÓÚÑÜ¿¡]")

SPANISH_WORDS = frozenset("""
acta actas adjunto adjuntos agregado ahora anterior archiva archivado archivar arbol archivo
ayer abre abrio abierto bloqueado borde busqueda buscar
calculando campos cancelar cargada cargadas cargando celdas ciclo coincidencias cobertura completa conectado
conectando conecta crea creado crear
dano deshacer descendientes descripcion desplaza dibujar declaracion disponible documentos dueno
elimina enfoca enlace escribio esperado estado exportacion exportado exportando
fallida faltante
guardado guardar hace hijo hoy
iniciando inesperado ingresa inicio
limite limpiar leyendo listo
mapa mapas media mes metricas mostrar
navega nodo nodos nombre notas nuevo
pudo pude plantilla plantillas plegar presiona
quitado ramas recorrido restaura retomar riesgo ruta
sem siguiente sin sesion subarbol suspendidos suspendido
tardar territorio ultima
vacio vencen ver vista
con de del el en es la las los para por se un una
baja demasiado desde datos dentro falta
activa activo aparece archivados corresponde edita editar esta este nada ningun oculto puede quedaria raiz recorrer
reemplazara requerido resaltado restaurado salir selecciona primero supera tarda tardar
""".split())

#: Dict keys and ids are not copy; none today.
ALLOW: frozenset[str] = frozenset()


def _fold(text: str) -> str:
    import unicodedata

    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


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
        for token in re.findall(r"[^\W\d_]+", _fold(text)):
            if token.lower() in SPANISH_WORDS:
                hits.append((line, text, f"word {token.lower()!r}"))
                break
    return hits


@pytest.mark.parametrize("rel", FILES)
def test_no_spanish_user_facing_string(rel):
    source = (ROOT / rel).read_text(encoding="utf-8")
    hits = spanish_hits(source)
    assert hits == [], f"{rel}: Spanish string literals: {hits}"


def test_scanner_sees_what_it_claims():
    """Oracle control: the scan flags a planted word, a planted accent and an f-string part, and passes English."""
    assert spanish_hits("x = 'no se pudo guardar'") != []
    assert spanish_hits("x = f'archivo no encontrado: {n}'") != []
    assert spanish_hits("x = 'búsqueda'") != []
    assert spanish_hits("x = '¿archivar «x»?'") != []
    assert spanish_hits("x = ' ramas · '") != []
    assert spanish_hits("x = 'con_acta'") != []
    assert spanish_hits("x = 'vencen'") != []
    assert spanish_hits("x = '↩ retomar'") != []
    assert spanish_hits("x = 'selecciona un nodo primero'") != []
    assert spanish_hits("x = 'esta vista no se desplaza'") != []
    assert spanish_hits("x = 'raíz'") != []
    assert spanish_hits("x = 'delta porter lasso unity'") == []  # whole words only: no substring hits
    assert spanish_hits("x = 'file not found: a.csv'\ny = 'no matches'\nz = 'nodes'") == []
    assert spanish_hits('def f():\n    """no se pudo guardar"""\n') == []


# -- behaviour arms: what the operator reads, driven through the real methods ---------------------------------------
def test_confirm_and_prompt_binding_labels_are_lowercase_english():
    from mapper.app import ConstructScreen, _ConfirmScreen

    assert [b[2] for b in _ConfirmScreen.BINDINGS] == ["yes", "no", "no", "no"]
    assert [b[2] for b in ConstructScreen.BINDINGS] == ["cancel"]


def test_the_editor_binding_labels_are_lowercase():
    """EN1-REV-F4: the labels the editor shows were capitalised while the keymap's are not."""
    from mapper.screens.editor import EditorScreen

    assert [b[2] for b in EditorScreen.BINDINGS] == ["save", "cancel", "preview"]


def test_home_metrics_hero_and_microbar_read_in_english(tmp_path):
    from datetime import date

    from mapper.app import HomeScreen
    from mapper.model import Ficha, Graph, Node

    screen = HomeScreen()
    graph = Graph()
    today = date.today().isoformat()
    graph.add_node(Node(id="a", ficha=Ficha(title="a", fields={"D": "doc", "due": today})))
    graph.add_node(Node(id="b", ficha=Ficha(title="b", fields={"due": today})))
    graph.add_node(Node(id="c", ficha=Ficha(title="c")))
    metrics = screen._map_metrics(graph)
    assert (metrics["total"], metrics["with_record"], metrics["no_record"], metrics["due"]) == (3, 1, 2, 2)
    hero = screen._hero_text("demo", metrics).plain
    assert "nodes with no record" in hero and "▲ 2 due today" in hero, hero
    bar = screen._microbar_text(metrics).plain
    assert "with record 1" in bar and "no record 2" in bar and "coverage" in bar, bar


def test_the_home_door_notes_read_in_english():
    from mapper.app import HomeScreen

    assert HomeScreen._DOOR_NOTES == {
        "c": "opens a recent map",
        "p": "connects a repository",
        "n": "creates a new map",
        "t": "map from a template",
        "i": "CSV / TSV of nodes",
        "f": "process documents",
    }


def test_the_repo_screen_reads_stages_and_ages_in_english():
    from datetime import date, timedelta

    from mapper.app import RepoScreen
    from mapper.model import Edge, Ficha, Graph, Node

    screen = RepoScreen("owner/name")
    stages = screen._stages_text().plain
    for word in ("starting", "reading branches", "computing metrics", "ready"):
        assert word in stages, stages
    graph = Graph()
    graph.add_node(Node(id="root", ficha=Ficha(title="r")))
    graph.root_id = "root"
    for key, age in {"b0": 0, "b1": 1, "b3": 3, "b14": 14, "b65": 65}.items():
        stamp = (date.today() - timedelta(days=age)).isoformat()
        graph.add_node(Node(id=key, ficha=Ficha(title=key, fields={"date": stamp})))
        graph.add_edge(Edge("root", key))
    graph.add_node(Node(id="nodate", ficha=Ficha(title="nodate")))
    graph.add_edge(Edge("root", "nodate"))
    screen.graph = graph
    table = screen._render_table().plain
    for want in ("today", "yesterday", "3 d ago", "2 wk ago", "2 mo ago", "no data", "6 branches", "(30 days)"):
        assert want in table, (want, table)
    screen.graph = Graph()
    assert screen._render_table().plain == "(no branches loaded)"


@pytest.mark.asyncio
async def test_archiving_reads_in_english_and_names_the_whole_map_refusal(tmp_path):
    from mapper.app import MapperApp, MapScreen, _ConfirmScreen
    from mapper.model import Edge, Ficha, Graph, Node

    graph = Graph()
    for nid, title in (("root", "erp"), ("a", "alfa"), ("b", "beta"), ("b1", "beta uno")):
        graph.add_node(Node(id=nid, ficha=Ficha(title=title)))
    for parent, child in (("root", "a"), ("root", "b"), ("b", "b1")):
        graph.add_edge(Edge(parent, child))
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        app.store.save("m", graph)
        app.push_screen(MapScreen("m"))
        await pilot.pause()
        await pilot.pause()
        screen = app.screen
        notes: list[str] = []
        screen.notify = lambda message, **kwargs: notes.append(message)  # the toast text, not a toast
        screen.nav.cursor = "a"
        await pilot.press("x")
        await pilot.pause()
        assert isinstance(app.screen, _ConfirmScreen)
        assert app.screen.message == "archive «alfa»?"
        await pilot.press("n")
        await pilot.pause()
        screen.nav.cursor = "b"
        await pilot.press("x")
        await pilot.pause()
        assert app.screen.message == "archive «beta» and its 1 descendants?"
        await pilot.press("n")
        await pilot.pause()
        screen.nav.cursor = "root"
        await pilot.press("x")
        await pilot.pause()
        assert notes == [
            "cannot archive the whole map: it would be empty. archive a branch, or delete the map from home."
        ], notes


@pytest.mark.asyncio
async def test_the_csv_missing_file_toast_names_the_file_coerced_and_not_the_path(tmp_path, monkeypatch):
    """The English sentence keeps the `darkside.plain` coercion: a right-to-left override in a typed name never
    reaches the toast raw, and the typed directory is never echoed (only the file's name)."""
    from mapper.app import MapperApp, _PromptScreen

    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    typed = str(tmp_path / "miss\u202eing.csv")
    app = MapperApp(tmp_path)
    toasts: list[str] = []
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        real_notify = app.notify

        def notify(message, **kwargs):
            toasts.append(str(message))
            return real_notify(message, **kwargs)

        app.notify = notify
        await pilot.press("i")
        await pilot.pause()
        assert isinstance(app.screen, _PromptScreen), app.screen
        app.screen.query_one("#prompt-input").value = typed
        await pilot.press("enter")
        for _ in range(6):
            await pilot.pause()
    assert toasts == ["file not found: miss\ufffding.csv"], toasts
    assert not any("\u202e" in t or str(tmp_path) in t for t in toasts), toasts
