"""OOXML office-template ingestion and resolution.

Supports .docx, .pptx and .xlsx files that contain ``{{keyword}}`` placeholders.
Read with stdlib ``zipfile`` + ``re``; write back by string-replacing placeholders
inside the XML members and rezipping. Fragmented tags are handled by
concatenating text runs per paragraph before matching.
"""
from __future__ import annotations

import re
import xml.sax.saxutils as saxutils
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


def _xml_escape(value: str) -> str:
    """Escape characters that break OOXML text runs."""
    return saxutils.escape(value)


def _resolve_docx_paragraph(para_xml: str, tags: dict[str, str]) -> str:
    """Resolve tags inside a single docx paragraph XML fragment.

    Concatenates all <w:t> text runs, replaces tags, then distributes the
    result back into the runs. This handles tags split across runs or with
    whitespace inside the braces.
    """
    # Extract runs while preserving their XML wrappers.
    runs: list[tuple[str, str]] = []
    pos = 0
    for match in re.finditer(r"(<w:t[^>]*>)([^<]*)(</w:t>)", para_xml):
        prefix, text, suffix = match.groups()
        runs.append((prefix + text + suffix, text))
        pos = match.end()

    if not runs:
        return para_xml

    # Concatenate plain text and resolve tags.
    full_text = "".join(text for _, text in runs)
    resolved_text = full_text
    for key, value in tags.items():
        # Tolerate whitespace inside braces: {{ key }} matches key.
        pattern = re.compile(r"\{\{\s*" + re.escape(key) + r"\s*\}\}")
        resolved_text = pattern.sub(_xml_escape(value), resolved_text)

    if resolved_text == full_text:
        return para_xml

    # Distribute resolved text back into the first run; clear the rest.
    # This preserves styles on the first run and keeps the paragraph valid.
    first_run_prefix, first_run_suffix = runs[0][0].split(runs[0][1], 1)
    out = [first_run_prefix + resolved_text + first_run_suffix]
    for run_xml, _ in runs[1:]:
        prefix, suffix = run_xml.split("</w:t>", 1)
        # Keep the XML wrapper but empty the text content.
        tag_open = prefix[: prefix.index(">") + 1]
        out.append(tag_open + suffix)
    return "".join(out)


def _resolve_text_xml(text: str, tags: dict[str, str]) -> str:
    """Resolve tags in a generic XML text string (pptx/xlsx)."""
    resolved = text
    for key, value in tags.items():
        pattern = re.compile(r"\{\{\s*" + re.escape(key) + r"\s*\}\}")
        resolved = pattern.sub(_xml_escape(value), resolved)
    return resolved


def resolve(path: Path, tags: dict[str, str], target: Path) -> Path:
    """Create a resolved copy of *path* at *target* with tags replaced.

    For .docx, tags are resolved per paragraph by collapsing text runs, which
    handles fragmentation and whitespace inside braces. Replacement values are
    XML-escaped before insertion.
    """
    kind = _kind_from_path(path)
    if not kind:
        raise ValueError(f"unsupported office file: {path}")

    members = set(_text_members(kind))
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "r") as zin:
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename in members:
                    text = data.decode("utf-8")
                    if kind == "docx":
                        # Process each <w:p>...</w:p> paragraph.
                        parts = re.split(r"(</w:p>)", text)
                        resolved_parts = []
                        for i, part in enumerate(parts):
                            if i % 2 == 1:
                                # This is the closing tag itself.
                                resolved_parts.append(part)
                            else:
                                resolved_parts.append(_resolve_docx_paragraph(part, tags))
                        text = "".join(resolved_parts)
                    else:
                        text = _resolve_text_xml(text, tags)
                    data = text.encode("utf-8")
                zout.writestr(item, data)
    return target
