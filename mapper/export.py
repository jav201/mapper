"""Export current view to SVG/PNG."""
from __future__ import annotations

import io
from pathlib import Path

from rich.console import Console
from rich.text import Text


class ExportError(Exception):
    pass


def save_svg(text: Text, path: Path | str) -> None:
    """Capture a Rich Text to SVG."""
    console = Console(record=True, width=200, height=60, file=io.StringIO())
    console.print(text)
    console.save_svg(str(path), title="mapper")


def save_png(text: Text, path: Path | str) -> None:
    """Best-effort PNG export via cairosvg if available."""
    try:
        import cairosvg
    except ImportError as exc:
        raise ExportError("cairosvg not installed; install mapper[export]") from exc

    svg_path = Path(path).with_suffix(".svg")
    save_svg(text, svg_path)
    cairosvg.svg2png(url=str(svg_path), write_to=str(path))
