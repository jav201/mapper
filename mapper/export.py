"""Export current view to SVG/PNG."""
from __future__ import annotations

import io
from pathlib import Path

from rich.cells import cell_len
from rich.console import Console
from rich.text import Text


class ExportError(Exception):
    pass


class ExportTooLarge(ExportError):
    """The map's extent exceeds the export budget, so NOTHING is written.

    Carries the numbers the refusal has to show the operator: a refusal that
    says only "too big" leaves them with no way to judge how much too big, or
    whether focusing a subtree would be enough.
    """

    def __init__(self, cells: int, limit: int):
        self.cells = cells
        self.limit = limit
        super().__init__(f"export extent {cells} cells exceeds the {limit}-cell budget")


def save_svg(text: Text, path: Path | str) -> None:
    """Capture a Rich Text to SVG, sized to the text it was handed.

    THE WIDTH IS MEASURED, NOT ASSUMED, AND THE CONSTANT IT REPLACES WAS A
    SILENT MANGLER.  This console was built at a hard-coded `width=200`, which
    was invisible while the caller sized its render from the terminal.  Once the
    export began sizing from the MAP, an ordinary map exceeded it -- a full
    extent is 241 columns at 21 nodes -- and Rich FOLDS every row past the
    console width into stacked chunks in row-major order.  The artifact kept
    every title, stayed a well-formed SVG, and lost the tree's adjacency: a file
    that looks complete and is not, which is the exact defect class the export
    ruling exists to refuse, one layer below where it was ruled.

    `cell_len`, never `len`: Rich measures in terminal CELLS, and this picture
    is full of box-drawing and wide glyphs whose code-point count is not their
    printed width.  A `len`-derived width would fold again, more rarely and more
    confusingly.

    THE `+ 1` IS MEASURED AND LOAD-BEARING, not defensive padding.  A line whose
    width is EXACTLY the console width still wraps: measured on a 245-cell
    header at `width=245`, the tail `21 nodos` was emitted as its own row -- so
    the widest line in the picture, which is the one that SETS the width, was
    the one line guaranteed to fold.  At `width=246` nothing splits.  Sizing to
    the measured maximum alone would have fixed every row except the one it was
    derived from, which is the kind of near-miss that reads as success.
    """
    lines = text.plain.split("\n")
    width = max(20, max((cell_len(line) for line in lines), default=20)) + 1
    height = max(1, len(lines))
    console = Console(record=True, width=width, height=height, file=io.StringIO())
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
