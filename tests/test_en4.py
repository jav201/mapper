"""Inc-EN-4 -- census arm over `store.py`, `darkside.py` and `widgets/components.py`, plus the `Z1` arms.

Authority: `VERDICT-inc-en-2026-10-02.md` (EN-Q1, EN-Q2, Z1) and `VERDICT-inc8-legend-2026-09-28.md` section LANGUAGE RULING.
Same method as `test_en2.py` / `test_en3.py`: the arm reads each file's AST, skips docstrings and comments, and fails on
any string literal that holds an accented character or a word from SPANISH_WORDS (whole words, never substrings).  The
list is explicit so a reviewer can read what the arm can and cannot see; it does not claim to detect Spanish in general.
`widgets/inspector.py` is in the Z1 arm only (it passes `toggle=False`); its own census was EN-2's.
"""
from __future__ import annotations

import ast
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILES = (
    "mapper/store.py",
    "mapper/darkside.py",
    "mapper/widgets/components.py",
)

ACCENTED = re.compile("[áéíóúñüÁÉÍÓÚÑÜ¿¡]")

SPANISH_WORDS = frozenset("""
acta actas arbol aristas completo conteos cobertura dibujo eliminados etiquetas fichas fuera limite listado mapa
nodo nodos omitio rama ramas supera vista
con de del el en es etiqueta la las los ningun ninguna ninguno nombre para por se sin un una y
adjunto adjuntos auditoria campo campos caracteres ciclo criticidad cargando demasiado desincronizado documento
duplicado dueno elige empezar espacio estado existe fantasma ficha hijo hoy ilegible indexar largo leer letra
maximo navega notas nomina nuevo omitidos otro presiona primer pudo punto registros reservado retomar ruta
segundo separadores sobrescribe terminar unidad validos vencen ver vacio ya
""".split())

#: Windows device names are not Spanish: `CON` is the console (`store._RESERVED_NAMES`).
DEVICE_TOKENS = frozenset({"CON"})
#: On-disk file name, not copy: the sidecar of every saved map is `<id>_nodos.yml`, so renaming it would orphan them.
FILE_FORMAT_LITERALS = frozenset({"_nodos.yml"})


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
        if text in FILE_FORMAT_LITERALS:
            continue
        if ACCENTED.search(text):
            hits.append((line, text, "accented character"))
            continue
        for token in re.findall(r"[^\W\d_]+", text):
            if token in DEVICE_TOKENS:
                continue
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
    assert spanish_hits("x = 'el nombre del mapa está vacío'") != []
    assert spanish_hits("x = 'campo ilegible: '") != []
    assert spanish_hits("x = f'nodo fantasma: {n}'") != []
    assert spanish_hits("x = 'dueño'") != []
    assert spanish_hits("x = '▽ 35 fuera de vista'") != []
    assert spanish_hits("x = '▲ 2 vencen hoy'") != []
    assert spanish_hits("x = 'navega con j/k'") != []
    assert spanish_hits("x = 'nombre del mapa…'") != []
    assert spanish_hits("x = '◫ ACTA-7'") != []
    assert spanish_hits("x = 'delta porter lasso unity'") == []  # whole words only: no substring hits
    assert spanish_hits("x = 'the map name uses a reserved Windows name (CON, NUL, COM1...)'") == []
    assert spanish_hits("x = '_nodos.yml'") == []  # the sidecar file-name format, exact literal only
    assert spanish_hits("x = '_nodos.yml!'") != []
    assert spanish_hits("x = 'con'") != []  # the device exemption is the upper-case token only
    assert spanish_hits("x = 'owner'\ny = 'legacy audit'\nz = '◫ no record'") == []
    assert spanish_hits('def f():\n    """campo ilegible del mapa"""\n') == []


def test_map_id_messages_read_in_english_and_echo_nothing_new():
    """The seven `MapIdError` sentences, driven through `check_map_id` (the rule itself is unchanged)."""
    from mapper.store import MapIdError, check_map_id

    cases = {
        "": "the map name is empty",
        "x" * 101: "the map name is too long (maximum 100 characters)",
        "zq/zq": "the map name cannot contain path separators",
        "zq?zq": "the map name contains characters that are not valid on Windows",
        "a\udc80b": "the map name contains characters that cannot be saved to a file",
        "NUL": "the map name uses a reserved Windows name",
        " zqzq": "the map name cannot start with a space or end with a dot or a space",
    }
    for map_id, want in cases.items():
        with pytest.raises(MapIdError) as exc:
            check_map_id(map_id)
        text = str(exc.value)
        assert want in text, (map_id, text)
        assert not ACCENTED.search(text), text
        if "zq" in map_id:
            assert map_id not in text, (map_id, text)  # nothing of the rejected id is echoed


def test_seed_content_is_english(tmp_path):
    """EN-Q2: the new-map seed and the `legacy-audit` template are written in English."""
    from mapper.store import MapStore

    store = MapStore(tmp_path)
    graph = store.create_seed("seed")
    assert graph.nodes["root"].ficha.meta == "new map"
    assert [graph.nodes[i].ficha.title for i in ("n1", "n2")] == ["first child", "second child"]
    assert [graph.nodes[i].ficha.meta for i in ("n1", "n2")] == ["press l", "navigate with j/k"]
    graph = store.create_from_template("tpl", "legacy-audit")
    assert [f.label for f in graph.schema] == ["document", "owner", "state", "criticality", "notes"]
    assert graph.nodes["root"].ficha.title == "legacy audit"


# -- Z1: an attachment chip only opens; it never toggles `selected` ------------------------------------------------
@pytest.mark.asyncio
async def test_z1_activating_a_chip_that_does_not_toggle_leaves_selected_and_look_unchanged():
    from textual.app import App

    from mapper.widgets.components import DsChip

    class Host(App):
        def __init__(self):
            super().__init__()
            self.seen = []

        def compose(self):
            yield DsChip(label="doc", toggle=False, id="c")

        def on_ds_chip_changed(self, event):
            self.seen.append(event.selected)

    app = Host()
    async with app.run_test() as pilot:
        chip = app.query_one("#c", DsChip)
        chip.focus()
        await pilot.pause()
        before = repr(chip.render())
        await pilot.press("enter")
        await pilot.press("enter")
        await pilot.pause()
        assert chip.selected is False
        assert repr(chip.render()) == before
        assert app.seen == [False, False]  # it still announces the activation, twice


@pytest.mark.asyncio
async def test_z1_the_default_chip_still_toggles():
    from textual.app import App

    from mapper.widgets.components import DsChip

    class Host(App):
        def compose(self):
            yield DsChip(label="legacy", id="c")

    app = Host()
    async with app.run_test() as pilot:
        chip = app.query_one("#c", DsChip)
        chip.focus()
        await pilot.pause()
        await pilot.press("enter")
        assert chip.selected is True
        await pilot.press("enter")
        assert chip.selected is False


@pytest.mark.parametrize("key", ["enter", "space"])
async def test_z1_opening_an_attachment_chip_twice_with_real_keys_leaves_selected_false(key, tmp_path, monkeypatch):
    """The inspector's own `insp-att-*` chips, driven by real `tab` and `enter` / `space`: the open still happens
    (twice) and the chip's `selected` and look are what they were."""
    from mapper.app import MapperApp
    from mapper.model import Attachment
    from mapper.widgets.components import DsChip
    from tests.test_attachments import RecordingLauncher, _open, _seed
    from tests.test_inc9f import SIZE
    from tests.test_inc9m import _env
    from tests.test_inc9x3 import _focus_chip

    _env(monkeypatch, tmp_path)
    (tmp_path / "docs").mkdir(exist_ok=True)
    (tmp_path / "docs" / "x.pdf").write_bytes(b"%PDF-1.4\n")
    app = MapperApp(tmp_path)
    launcher = RecordingLauncher()
    app.attachment_launcher = launcher
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await _open(app, pilot, _seed(app, [Attachment(kind="file", path="docs/x.pdf", caption="plan")]))
        await _focus_chip(app, pilot, 0, SIZE)
        chip = app.focused
        assert isinstance(chip, DsChip) and chip.id == "insp-att-0", chip
        before = repr(chip.render())
        for _ in range(2):
            await pilot.press(key)
            for _ in range(3):
                await pilot.pause()
            assert chip.selected is False  # after EACH open: two toggles would also end False, so look in between
            assert repr(chip.render()) == before
        resolved = str((tmp_path / "docs" / "x.pdf").resolve())
        assert launcher.calls == [resolved, resolved], launcher.calls
        assert chip.selected is False
        assert repr(chip.render()) == before
