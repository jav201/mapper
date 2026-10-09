"""Inc-1b renders (UX-1 / PDR C6): composited frames at 87, 118 and 140 columns.

Run from the worktree root: python -B <this> > inc1b-renders.txt
States per width: the map at rest (keybar), a two-field draft with the card
visible, the same draft with the card hidden (the hint-line prefix), and the
node-change guard.  The 118 "before" keybar is the same frame with the seat's
`ctrl+s` row removed (the keybar is derived only from the seat).
"""
import asyncio, sys, tempfile
from pathlib import Path

sys.path.insert(0, ".")
from mapper import keymap  # noqa: E402
from mapper.app import MapperApp  # noqa: E402
from tests.inc3_support import frame_rows  # noqa: E402
from tests.test_draft_save import _open, _press, _seed_map, _type_into  # noqa: E402


def dump(title, screen):
    print(f"--- {title} ---")
    for row in frame_rows(screen):
        print(row.rstrip())
    print()


async def frames(width, *, label=""):
    app = MapperApp(Path(tempfile.mkdtemp()))
    async with app.run_test(size=(width, 34)) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed_map(app))
        dump(f"{width} cols{label} · at rest", screen)
        if label:
            return
        if screen.inspector_hidden:
            await _press(pilot, "I")
        await _type_into(pilot, screen, "insp-title", "x")
        await _type_into(pilot, screen, "insp-field-D", "y")
        await _press(pilot, "escape")
        dump(f"{width} cols · draft of two fields, card visible", screen)
        await _press(pilot, "I")
        dump(f"{width} cols · same draft, card hidden (hint-line prefix, ALERT)", screen)
        await _press(pilot, "I")
        await _press(pilot, "j")
        dump(f"{width} cols · j with the draft: the guard", app.screen)
        await _press(pilot, "escape")


async def main():
    real = keymap.KEYMAP
    keymap.KEYMAP = [b for b in real if b.action != "save_draft"]
    try:
        await frames(118, label=" BEFORE (seat without the ctrl+s row)")
    finally:
        keymap.KEYMAP = real
    for width in (87, 118, 140):
        await frames(width)


asyncio.run(main())
