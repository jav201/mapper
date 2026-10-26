# Seam probe (a) — AT driver host push + fixture workspace injection

- Date: 2026-10-25
- Batch: `2026-10-25-relmap-r2-batch` (branch `feat/relmap-r2`, worktree `wt-r2`)
- Seam under test: an acceptance test drives the real `MapperApp` through Textual's `Pilot` and injects a temporary fixture workspace. Contract flagged this `assumed — verify in Phase 2`.

## Mechanism found

Workspace injection is a **constructor argument**, not an env var and not a default-dir mutation:

- `mapper/app.py:250` — `def __init__(self, workspace: Path | str):`
- `mapper/app.py:256` — `self.store = MapStore(workspace)` (the only consumer of the argument)
- `mapper/app.py:355` — the production CLI does `MapperApp(Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / "maps")`; there is no `MAPPER_WORKSPACE`-style env var anywhere.
- `mapper/screens/home.py:209` — Home discovers maps via `store.workspace.glob("*.mmd")`; `mapper/store.py:763` pairs each `<id>.mmd` with `<id>_nodos.yml` (the descriptor file) at load time. A `.mmd` without its `_nodos.yml` still loads (kind `concept`); with it, kind is `legacy` and the graph carries the schema.
- Pilot idiom precedent: `tests/test_colour_always_on.py:64-70` — `async with app.run_test(size=SIZE) as pilot:` around a real `MapperApp(tmp_path)`, plus `await pilot.pause()` / `pilot.wait_for_scheduled_animations()`.

## Probe script

Exact script as run (final, green version). Lives at `<scratch>/probe_seam_at_driver.py` (deleted after the run per probe rules).

```python
"""Seam probe (a): AT-driver host push + fixture workspace injection.

Proves a Textual Pilot can run the real MapperApp pointed at a temporary
fixture workspace, reach the Home screen, and observe relation-map rows.

Fixture content uses neutral synthetic names only (svc-a, svc-b, db-c, team-x).
"""
from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from textual.widgets import DataTable, Static

from mapper.app import MapperApp
from mapper.screens.home import HomeScreen

SCRATCH = Path(__file__).parent

MMD = """graph TD
    svc-a[Svc A] --> svc-b[Svc B]
    svc-a --> db-c[Db C]
"""

NODOS = """schema:
  - key: D
    label: documento
    required: true
  - key: O
    label: dueno
    required: false

nodes:
  svc-a:
    title: Svc A
    state: ok
    fields:
      D: ACTA-2026-001
      O: team-x
  svc-b:
    title: Svc B
    state: risk
    fields:
      D: ACTA-2026-002
      O: team-y
  db-c:
    title: Db C
    state: ok
    fields:
      D: ACTA-2026-003
"""


def build_workspace(root: Path) -> Path:
    ws = root / "ws"
    ws.mkdir()
    (ws / "svc_probe.mmd").write_text(MMD, encoding="utf-8")
    (ws / "svc_probe_nodos.yml").write_text(NODOS, encoding="utf-8")
    return ws


async def main() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="seam-probe-", dir=SCRATCH))
    ws = build_workspace(tmp)
    print(f"[probe] tmp workspace: <scratch>/.../{tmp.name}")

    # The injection point under test: MapperApp(workspace=tmp fixture dir).
    app = MapperApp(ws)
    assert app.store.workspace == ws, "store workspace is not the injected one"
    print("[probe] MapperApp constructed with injected tmp workspace: OK")

    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        assert isinstance(app.screen, HomeScreen), (
            f"expected HomeScreen, got {type(app.screen).__name__}"
        )
        print("[probe] Home screen reached via Pilot: OK")

        table = app.screen.query_one("#home-recents", DataTable)
        rows = [
            [str(c) for c in table.get_row_at(i)]
            for i in range(table.row_count)
        ]
        print(f"[probe] recents table rows: {rows!r}")
        assert table.row_count == 1, f"expected 1 row, got {table.row_count}"
        name, kind, nodos, docs = rows[0]
        assert name.strip() == "svc_probe", f"unexpected row name {name!r}"
        assert "legacy" in kind, f"expected legacy kind cell, got {kind!r}"
        assert nodos.strip() == "3", f"expected 3 nodes, got {nodos!r}"
        print("[probe] relation-map row observed (name/kind/nodes): OK")

        # Cross-check the store derivation seam itself on the same workspace.
        graph = app.store.load("svc_probe")
        assert len(graph.nodes) == 3 and graph.schema, "store.load seam mismatch"
        print(f"[probe] store.load('svc_probe'): {len(graph.nodes)} nodes, "
              f"{len(graph.schema)} schema fields: OK")

        hero = app.screen.query_one("#home-hero", Static)
        hero_text = str(hero.render())
        assert "svc_probe" in hero_text, "map name not visible in home hero"
        print("[probe] home hero carries the map name: OK")

    print("[probe] exited cleanly: OK")
    print("PROBE-RESULT: PASS")


if __name__ == "__main__":
    asyncio.run(main())
```

## Run transcript

Command (run from the worktree root; only the scratch path is referenced, shown sanitized):

```
PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 python <scratch>/probe_seam_at_driver.py
```

Output (final run, exit code 0):

```
[probe] tmp workspace: <scratch>/.../seam-probe-ws8a6mq2
[probe] MapperApp constructed with injected tmp workspace: OK
[probe] Home screen reached via Pilot: OK
[probe] recents table rows: [['svc_probe', ' legacy ', '3', '0']]
[probe] relation-map row observed (name/kind/nodes): OK
[probe] store.load('svc_probe'): 3 nodes, 2 schema fields: OK
[probe] home hero carries the map name: OK
[probe] exited cleanly: OK
PROBE-RESULT: PASS
```

Two earlier iterations failed on probe-side API guesses, not on the seam: (1) `DataTable.get_row_iter` does not exist in Textual 8.2.8 — `get_row_at(i)` is the API; (2) `App.export_text` does not exist in Textual 8.2.8 — replaced with a `#home-hero` `Static.render()` assertion. All seam-level assertions passed on the very first run.

## Result

**PASS.** The seam is viable on today's code. The contract should pin the concrete injection point as:

> ATs construct the app directly: `MapperApp(workspace=<tmp fixture dir>)` (positional or keyword `workspace: Path | str`, `mapper/app.py:250`), then drive it with `async with app.run_test(size=(w, h)) as pilot:`. No env var, no monkeypatching, no cwd games — `MapStore` reads the injected path and nothing else.

Observable for ATs: `app.screen` is `HomeScreen`; `#home-recents` (`DataTable`) lists one row per `*.mmd` in the workspace as `[name, kind, nodes, docs]` where kind is `legacy` when the paired `<id>_nodos.yml` descriptor parsed with a schema, else `concept`. The `#home-hero` Static carries the hero map's name.

## Notes

- Textual version in this worktree: **8.2.8**. `App.run_test()` works headless with no terminal; no Windows console needed. `PYTHONIOENCODING=utf-8` recommended on Windows (the app paints box-drawing glyphs).
- The fixture workspace needs no seeding beyond the two files: `MapStore` rebuilds `mapper.db` from `.mmd` + `_nodos.yml` (comment at `mapper/store.py:412`). A bare `.mmd` also works (kind `concept`) but the descriptor exercises the relmap-relevant path.
- `run_test(size=(120, 40))` is enough for the home layout; the codebase's wider precedent uses `WIDE_SIZES[0]` from `tests/test_repair_layout.py`.
- Probe script and its temp workspaces were deleted from `<scratch>` after the run; this transcript is the only retained artifact.
- Not probed (out of scope here): pushing screens past Home (e.g. `MapScreen`) from an AT, and `derive_reqharness_map(workspace, default_descriptor())` — that entry point targets a *requirements repo* (`mapper/relmap/adapter.py:121`), not the TUI workspace; it is a separate seam.
