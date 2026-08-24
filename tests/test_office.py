"""Tests for mapper.office OOXML template ingestion."""
from __future__ import annotations

import zipfile
from pathlib import Path

from mapper import office


def _make_docx(path: Path, text_xml: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", "<?xml version='1.0' encoding='UTF-8' standalone='yes'?><Types/>")
        zf.writestr("word/document.xml", text_xml)


def test_extract_tags_from_docx(tmp_path):
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:p><w:r><w:t>{{nombre}}</w:t></w:r></w:p>'
        '<w:p><w:r><w:t>{{puesto}}</w:t></w:r><w:r><w:t> fijo</w:t></w:r></w:p>'
        '</w:document>'
    )
    path = tmp_path / "plantilla.docx"
    _make_docx(path, xml)

    tags = office.extract_tags(path)
    assert sorted(tags) == ["nombre", "puesto"]


def test_resolve_docx_replaces_tags(tmp_path):
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:p><w:r><w:t>Hola {{nombre}}, tu puesto es {{puesto}}.</w:t></w:r></w:p>'
        '</w:document>'
    )
    source = tmp_path / "plantilla.docx"
    _make_docx(source, xml)

    target = tmp_path / "out.docx"
    office.resolve(source, {"nombre": "Ana", "puesto": "dev"}, target)

    with zipfile.ZipFile(target, "r") as zf:
        resolved = zf.read("word/document.xml").decode("utf-8")
    assert "Hola Ana, tu puesto es dev." in resolved
    assert "{{nombre}}" not in resolved


def test_extract_preview_text(tmp_path):
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document><w:body><w:p><w:r><w:t>Primer párrafo</w:t></w:r></w:p>'
        '<w:p><w:r><w:t>Segundo párrafo</w:t></w:r></w:p></w:body></w:document>'
    )
    path = tmp_path / "doc.docx"
    _make_docx(path, xml)

    preview = office.extract_preview_text(path)
    assert "Primer párrafo" in preview
    assert "Segundo párrafo" in preview
