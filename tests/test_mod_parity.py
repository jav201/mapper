"""AT-065 / LLR-MOD.4.2 (HLR-MOD.4): painted-output parity against a text golden.

The honest oracle for "the split changed nothing" on a TUI is the painted
screen itself.  This module drives the real app with REAL KEYS through one
scripted session -- open a map, move, search, toggle the outline, export,
quit -- and records the visible characters of every row after each step, at
118 and 87 columns (height 34).  The captures are the committed goldens
`.dev-flow/2026-10-09-modular-batch/evidence/mod_parity_{118,87}.txt`; every
later increment re-runs the same session and must paint byte-identical lines.

Capture method (documented per the unit contract): `app.screen._compositor.
render_strips()` returns one Strip per terminal row; joining each strip's
segment texts yields the visible characters of that row.  `export_screenshot`
is SVG and unreadable as lines, so the compositor strips are the oracle --
the same seam `tests/test_draft_save.py` already reads (`_hint_text_and_
prefix_style`).

Volatile cells are normalised BEFORE comparison (LLR-MOD.4.2): the tmp
workspace path and any absolute path become `<ws>`, ISO dates, clock times
and the home identity's moon-phase glyph (a function of `date.today()`,
i.e. wall clock) become `<time>`.

The RED side is permanent (C5 mutant mechanism): a copy of the `mapper`
package with ONE painted string token changed is captured in a SUBPROCESS
(`PYTHONPATH` pointed at the copy) and its painted output must DIFFER from
the golden.  "golden file missing" is not the negative control, so the
on-disk golden's sha256 is pinned in `GOLDEN_SHA256` and asserted too.
"""
from __future__ import annotations

import difflib
import hashlib
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from mapper import darkside
from mapper.app import MapperApp

from tests.test_draft_save import _open, _press, _seed_map

REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = REPO_ROOT / ".dev-flow" / "2026-10-09-modular-batch" / "evidence"
HEIGHT = 34
WIDTHS = (118, 87)

#: Filled in after the goldens are captured at Inc-0 (see MOD_PARITY_UPDATE).
#: LLR-MOD.4.2 golden record: the on-disk golden must still hash to these.
GOLDEN_SHA256 = {
    118: "43af8e1e7613f23e9da0b9a3090c880c6b6f1cc0341f9befb8e032efd95fbf2d",
    87: "6ba755535f102742931c93af98a54889ea4ecc6e132f43a1db78f8461a889b9b",
}

#: The mutant's one-token change: a PAINTED string constant in app.py
#: (`SEARCH_COUNT_SUBJECT` -- the live-search count line our session paints).
_MUTANT_NEEDLE = 'SEARCH_COUNT_SUBJECT = "matches in the map"'
_MUTANT_REPLACEMENT = 'SEARCH_COUNT_SUBJECT = "hits in the map"'

_ABS_PATH = re.compile(r"[A-Za-z]:[\\/][^\s]*")
_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_CLOCK = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")


def _golden_path(width: int) -> Path:
    return EVIDENCE_DIR / f"mod_parity_{width}.txt"


def _normalise(line: str, ws: Path) -> str:
    """Volatile cells -> stable tokens: paths to `<ws>`, time/date to `<time>`."""
    line = line.replace(str(ws), "<ws>").replace(ws.as_posix(), "<ws>")
    line = _ABS_PATH.sub("<ws>", line)
    line = _ISO_DATE.sub("<time>", line)
    line = _CLOCK.sub("<time>", line)
    # The home identity's moon glyph is a function of date.today() -- the one
    # painted wall-clock cell.  Only the identity row is rewritten, so a real
    # `●` draft marker elsewhere in the paint keeps its full oracle strength.
    moon = darkside.moon(date.today())[0]
    line = line.replace(f"{moon} mapper", "<time> mapper")
    return line.rstrip()


def _painted_lines(app, ws: Path) -> list[str]:
    """One entry per terminal row: the row's visible characters, normalised.

    The source is the screen compositor's rendered strips (the same seam
    `tests/test_draft_save.py` reads), NOT `export_screenshot` (SVG).
    """
    strips = app.screen._compositor.render_strips()  # noqa: SLF001
    return [_normalise("".join(seg.text for seg in strip), ws) for strip in strips]


async def _scripted_session(app, pilot, ws: Path) -> list[str]:
    """AT-065's scripted session; one capture after EACH step, gated on a
    condition (`pilot.pause` / an asserted state), never a wall-clock sleep."""
    lines: list[str] = []
    map_id = _seed_map(app)
    screen = await _open(app, pilot, map_id)
    lines += [f"=== step: open {map_id} ===", *_painted_lines(app, ws)]

    await _press(pilot, "j")
    assert screen.nav.cursor == "b", screen.nav.cursor
    lines += ["=== step: move j ===", *_painted_lines(app, ws)]

    await _press(pilot, "l")  # `b` has no child: a deliberate repaint no-op
    lines += ["=== step: move l ===", *_painted_lines(app, ws)]

    await _press(pilot, "slash")
    await _press(pilot, "a", "l", "f", "enter")
    assert screen._search_is_live()  # noqa: SLF001
    lines += ["=== step: search alf enter ===", *_painted_lines(app, ws)]

    await _press(pilot, "escape")
    assert not screen._search_is_live()  # noqa: SLF001
    lines += ["=== step: search escape ===", *_painted_lines(app, ws)]

    await _press(pilot, "o")
    assert screen.outline_mode
    lines += ["=== step: outline on ===", *_painted_lines(app, ws)]

    await _press(pilot, "o")
    assert not screen.outline_mode
    lines += ["=== step: outline off ===", *_painted_lines(app, ws)]

    await _press(pilot, "e")
    for _ in range(50):  # condition wait: the async export lands when the file does
        if (ws / f"{map_id}.svg").exists():
            break
        await pilot.pause()
    assert (ws / f"{map_id}.svg").exists(), "export wrote no svg"
    lines += ["=== step: export e ===", *_painted_lines(app, ws)]

    await _press(pilot, "q")
    lines += ["=== step: quit q (home) ===", *_painted_lines(app, ws)]
    return lines


async def _capture(width: int, ws: Path) -> list[str]:
    """Drive the scripted session at *width* x 34 and return the golden text.
    Runnable both inside pytest (`asyncio_mode = "auto"`) and, via
    `asyncio.run`, in the mutant test's plain-python subprocess."""
    app = MapperApp(ws)
    async with app.run_test(size=(width, HEIGHT)) as pilot:
        await pilot.pause()
        return await _scripted_session(app, pilot, ws)


def _update_mode() -> bool:
    return os.environ.get("MOD_PARITY_UPDATE") == "1"


@pytest.mark.parametrize("width", WIDTHS)
async def test_at065_parity_matches_golden(tmp_path, width):
    """LLR-MOD.4.2: the scripted session paints the committed golden, 0 diffs,
    and the on-disk golden still hashes to the recorded sha256."""
    lines = await _capture(width, tmp_path)
    golden_path = _golden_path(width)

    if _update_mode():
        golden_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    golden = golden_path.read_text(encoding="utf-8").splitlines()
    if not _update_mode():
        digest = hashlib.sha256(golden_path.read_bytes()).hexdigest()
        assert digest == GOLDEN_SHA256[width], (
            f"golden {golden_path.name} was tampered with: {digest}"
        )
    differing = sum(1 for a, b in zip(lines, golden) if a != b) + abs(
        len(lines) - len(golden)
    )
    assert differing == 0, "\n".join(
        list(difflib.unified_diff(golden, lines, "golden", "painted", lineterm=""))[:60]
    )


_SUBPROCESS_SCRIPT = r"""
import asyncio
import importlib.util
import sys

mut, repo, ws, width = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
spec = importlib.util.spec_from_file_location(
    "test_mod_parity", repo + "/tests/test_mod_parity.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
lines = asyncio.run(module._capture(width, __import__("pathlib").Path(ws)))
sys.stdout.write("\n".join(lines) + "\n")
"""


async def test_at065_parity_red_on_a_mutant_copy(tmp_path):
    """C5 mutant mechanism, the permanent executable RED: one painted string
    token changed in a tmp copy of the product must redden the comparison."""
    mut = tmp_path / "mut"
    shutil.copytree(REPO_ROOT / "mapper", mut / "mapper")
    app_py = mut / "mapper" / "app.py"
    source = app_py.read_text(encoding="utf-8")
    assert _MUTANT_NEEDLE in source, "mutant needle not found in app.py"
    app_py.write_text(source.replace(_MUTANT_NEEDLE, _MUTANT_REPLACEMENT, 1),
                      encoding="utf-8")

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"  # the capture is UTF-8; Windows defaults to cp1252
    env["PYTHONPATH"] = os.pathsep.join(
        [str(mut), str(REPO_ROOT), env.get("PYTHONPATH", "")]
    )
    result = subprocess.run(
        [sys.executable, "-B", "-c", _SUBPROCESS_SCRIPT,
         str(mut), str(REPO_ROOT), str(tmp_path / "ws"), "118"],
        capture_output=True, text=True, encoding="utf-8", env=env, timeout=180,
        cwd=mut,  # `-c` puts cwd first on sys.path: the mutant package must win
    )
    assert result.returncode == 0, result.stderr
    painted = result.stdout.splitlines()

    golden = _golden_path(118).read_text(encoding="utf-8").splitlines()
    assert painted != golden, (
        "the mutant painted byte-identical output -- the oracle is blind"
    )
