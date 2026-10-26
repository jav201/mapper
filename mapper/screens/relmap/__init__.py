"""The `RelMapScreen` package — `mapper/screens/relmap/` (batch
`2026-10-25-relmap-r2-batch`, trunk Inc-2).

`screen.py` owns the host; `base.py` owns the shared painters and the frozen
host↔renderer surface (D1); the three renderer modules (`matrix.py`,
`gaps.py`, `sheet.py`) land in lanes 3/4/5 against that surface.  This
`__init__` re-exports `RelMapScreen` — the `MapScreen` pattern
(`mapper/screens/map/__init__.py`): screens open the host from here, never
through `mapper.app` (LLR-MOD.6.2).
"""

from .screen import RelMapScreen

__all__ = ["RelMapScreen"]
