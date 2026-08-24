"""OOXML office-template ingestion and resolution.

Supports .docx, .pptx and .xlsx files that contain ``{{keyword}}`` placeholders.
Read with stdlib ``zipfile`` + ``re``; write back by string-replacing placeholders
inside the XML members and rezipping. Fragmented tags are handled by
concatenating text runs per paragraph before matching.
"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path


_TAG_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")

# XML members that carry user-visible text for each office kind.
_TEXT_MEMBERS: dict[str, list[str]] = {
    "docx": ["word/document.xml"],
    "pptx": ["ppt/slides/slide{}.xml"],
    "xlsx": ["xl/sharedStrings.xml"],
}


def _kind_from_path(path: Path) -> str:
    ext = path.suffix.lower()
    return {".docx": "docx", ".pptx": "pptx", ".xlsx": "xlsx"}.get(ext, "")


def _text_members(kind: str) -> list[str]:
    if kind == "docx":
        return ["word/document.xml"]
    if kind == "pptx":
        # Slides are numbered 1..N; include a reasonable range.
        return [f"ppt/slides/slide{i}.xml" for i in range(1, 101)]
    if kind == "xlsx":
        return ["xl/sharedStrings.xml"]
    return []


def _extract_member_text(archive: zipfile.ZipFile, member: str) -> str:
    try:
        data = archive.read(member).decode("utf-8")
    except KeyError:
        return ""
    # Strip XML tags to get a rough plain-text preview.
    text = re.sub(r"<[^>]+>", "", data)
    return text


def extract_preview_text(path: Path) -> str:
    """Return a rough plain-text preview of an OOXML file."""
    kind = _kind_from_path(path)
    if not kind:
        return ""
    preview: list[str] = []
    try:
        with zipfile.ZipFile(path, "r") as zf:
            for member in _text_members(kind):
                text = _extract_member_text(zf, member)
                if text:
                    preview.append(text)
    except (zipfile.BadZipFile, OSError):
        return ""
    return "\n".join(preview)


def extract_tags(path: Path) -> list[str]:
    """Return sorted unique ``{{tag}}`` names found in *path*."""
    kind = _kind_from_path(path)
    if not kind:
        return []
    found: set[str] = set()
    try:
        with zipfile.ZipFile(path, "r") as zf:
            for member in _text_members(kind):
                try:
                    data = zf.read(member).decode("utf-8")
                except KeyError:
                    continue
                # Concatenate text runs inside each paragraph to catch
                # fragmented tags, then search for tags.
                if kind == "docx":
                    paragraphs = re.split(r"</w:p>", data)
                    for para in paragraphs:
                        runs = re.findall(r"<w:t[^>]*>([^<]*)</w:t>", para)
                        para_text = "".join(runs)
                        found.update(_TAG_RE.findall(para_text))
                else:
                    found.update(_TAG_RE.findall(data))
    except (zipfile.BadZipFile, OSError):
        return []
    return sorted(found)


def resolve(path: Path, tags: dict[str, str], target: Path) -> Path:
    """Create a resolved copy of *path* at *target* with tags replaced.

    Fragments are handled by replacing across the whole XML member string;
    this works for tags that may be split across runs because the XML still
    contains the marker characters contiguously.
    """
    kind = _kind_from_path(path)
    if not kind:
        raise ValueError(f"unsupported office file: {path}")

    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "r") as zin:
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename in _text_members(kind):
                    text = data.decode("utf-8")
                    for key, value in tags.items():
                        text = text.replace(f"{{{{{key}}}}}", value)
                    data = text.encode("utf-8")
                zout.writestr(item, data)
    return target
