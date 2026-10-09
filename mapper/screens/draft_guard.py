"""The draft guard: one question asked before an unsaved card edit is dropped.

US-001 / HLR-003.  The modal answers with exactly one of three tokens, read from
the `draft` seat scope: `save` (`s`), `discard` (`d`), `stay` (`esc`).  It decides
nothing and writes nothing; the screen that pushed it acts on the token.
"""
from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static

from mapper import darkside
from mapper.keymap import SCOPE_DRAFT, bindings_for, textual_bindings


class DraftGuardScreen(ModalScreen[str]):
    """Modal `save · discard · stay`, dismissed with `"save"`, `"discard"` or `"stay"`."""

    BINDINGS = [
        Binding(key, action, label, priority=priority)
        for key, action, label, priority in textual_bindings(SCOPE_DRAFT)
    ]

    DEFAULT_CSS = f"""
    DraftGuardScreen {{
        align: center middle;
        background: {darkside.GROUND} 70%;
    }}
    #draft-guard-dialog {{
        width: 60;
        height: auto;
        background: {darkside.PANEL};
        padding: 1 2;
    }}
    #draft-guard-title {{
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }}
    #draft-guard-hints {{
        text-align: center;
    }}
    """

    def __init__(self, title: str, map_id: str = "") -> None:
        super().__init__()
        self.node_title = title
        self.map_id = map_id

    def sentence(self) -> str:
        """R9: `unsaved draft on «{title}» · {map_id}`, both parts through `plain`.

        `markup=False` alone leaves ESC in (it strips BEL/BS/VT/FF/CR only), and
        `plain` alone leaves `[@click=…]` live in a markup sink: the sink needs both.
        """
        text = f"unsaved draft on «{darkside.plain(self.node_title)}»"
        if self.map_id:
            text += f" · {darkside.plain(self.map_id)}"
        return text

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(self.sentence(), id="draft-guard-title", markup=False),
            Static(self._hints(), id="draft-guard-hints"),
            id="draft-guard-dialog",
        )

    @staticmethod
    def _hints() -> Text:
        pieces: list[tuple[str, str]] = []
        for index, row in enumerate(bindings_for(SCOPE_DRAFT)):
            if index:
                pieces.append(("   ", darkside.MUT))
            pieces.append((row.glyph, darkside.INK))
            pieces.append((f" {row.label}", darkside.MUT))
        return Text.assemble(*pieces)

    def action_save(self) -> None:
        self.dismiss("save")

    def action_discard(self) -> None:
        self.dismiss("discard")

    def action_stay(self) -> None:
        self.dismiss("stay")
