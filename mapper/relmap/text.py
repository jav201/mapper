"""The presentation leaf (HLR-RVT.1, LLR-RVT.1.1-.1.3; `PDR-2026-10-25-relmap-r2-batch#D2`).

`cut`, `DISPLAY_MAX` and `refusal_line` have ONE definition site here and ONE
import path (R1 DDR E 10-11, B-153): every consumer -- `model`, `descriptor`,
`audit`, `adapter` -- imports them from this leaf.  Stdlib-only: the leaf
imports nothing but `__future__`, so it sits below the whole package
(ARCHITECTURE `relmap` row).  The lines `refusal_line` returns are
repository-derived and UNESCAPED: the sink must escape them; the base name is
cut here.

The K5 cause is matched by its fixed text (`K5_CAUSE`, the closed cause set
K1-K17) rather than by importing `descriptor.CAUSE` -- the leaf may not import
the package, and `descriptor` imports the leaf.
"""
from __future__ import annotations

K5_CAUSE = "exceeds the byte limit"

DISPLAY_MAX = 120


def cut(text: str) -> str:
    """`text` in at most `DISPLAY_MAX` characters; a cut value ends with an ellipsis."""
    if len(text) <= DISPLAY_MAX:
        return text
    return text[: DISPLAY_MAX - 1] + "…"


def refusal_line(base_name: str, cause: str, limit: int | None = None) -> str:
    """`structure: refused (<base name>): <cause> - descriptor skipped`.  The base name is cut
    to 120 characters; K5 renders `exceeds the <limit> byte limit` when `limit` is given."""
    if cause == K5_CAUSE and limit is not None:
        cause = f"exceeds the {limit} byte limit"
    return f"structure: refused ({cut(base_name)}): {cause} - descriptor skipped"
