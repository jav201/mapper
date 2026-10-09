"""The editable ficha inspector — variant A «taller»'s right-hand panel.

This widget owns no persistence.  `docs/ARCHITECTURE.md` §3 bans `widgets → store`,
so an edit here only updates this widget's per-node draft (US-001, HLR-001): the
owning screen — which holds the graph and the store — reads the draft on `ctrl+s`
and makes the one whole-graph write.  Nothing here ever asks for a save.

Every value it renders comes from `_nodos.yml`, i.e. from a file a human edits by
hand and that may arrive with a cloned map.  So every such value passes through
`darkside.plain()` and is placed into a `Text` with an explicit style; no
file-derived string is ever handed to a markup-parsing sink (LLR-N01.10/N01.11).
"""
from __future__ import annotations

from textual.binding import Binding
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Input, Static

from mapper import darkside
from mapper.keymap import SCOPE_MAP, hint_pair
from mapper.model import Ficha, Graph, Node, SchemaField
from mapper.widgets.chrome import HintLine, KeyBar
from mapper.widgets.components import DsChip, DsProgress, DsSegmented

# The four states a ficha may carry: the stored value, and the word shown for it (the same four words).
STATE_VALUES = ["ok", "risk", "late", "blocked"]
STATE_LABELS = ["ok", "risk", "late", "blocked"]

# `Z2`: the word beside `↵` while an attachment chip holds focus.  The seat's own word
# for the key is `open card`, which is true everywhere except on a chip.
ATTACHMENT_OPEN_LABEL = "open attachment"

# The one style of the unsaved state: the header's `● unsaved (N)` and each dirty
# label's `●`.  WARN's declared job is "pending" (`darkside` docstring), which is
# exactly what an unsaved draft is (design 1b.7).
UNSAVED_STYLE = darkside.WARN

# Fixed column the inspector occupies beside the canvas.  The canvas subtracts it
# when sizing its render, so the two cannot overlap.
INSPECTOR_WIDTH = 36


class FieldInput(Input):
    """An inspector edit field that releases focus on `escape`.

    Without this, `escape` reaches `MapScreen`'s binding and pops the whole map,
    discarding what was typed — measured on the shipped app before this batch.
    A widget-level binding claims the key first, so `escape` means "leave the
    field, keep the value" while a field is focused, and "leave the map" when one
    is not.

    Focus does not select the value (`B-72`): Textual's default selects it all, so
    the first printable key -- `?` included -- replaced the whole title and saved it.
    """

    BINDINGS = [Binding("escape", "leave_field", "leave the field")]

    def __init__(self, *args, node_id: str | None = None, **kwargs) -> None:
        kwargs.setdefault("select_on_focus", False)
        super().__init__(*args, **kwargs)
        # The node this input was built for, so a change that arrives after the
        # inspector re-pointed can be recognised as stale (LLR-001.2).
        self.node_id = node_id

    class Left(Message):
        """The operator stepped out of a field without abandoning the value."""

    def action_leave_field(self) -> None:
        self.post_message(self.Left())


class FichaInspector(Vertical):
    """Editable form for the selected node's ficha."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.node: Node | None = None
        self.schema: list[SchemaField] = []
        self._pending_focus: str | None = None
        # `Z2`: what the hint line and the key bar said before a chip took focus, as
        # (hint, groups) -- each None when that surface was not touched.
        self._chip_override: tuple[str | None, list | None] | None = None
        # The draft (LLR-001.1): DIRTY entries only, keyed by a schema key or one
        # of the pseudo-keys `title` / `notes` / `state`.  In memory, never saved
        # from here.
        self._draft_node_id: str | None = None
        self._draft: dict[str, str] = {}
        # field -> (its label Static, the label text, required-and-missing), so the
        # dirty markers repaint in place without a remount (LLR-002.2).
        self._labels: dict[str, tuple[Static, str, bool]] = {}

    # -- rendering ---------------------------------------------------------
    # No `compose`: the form's shape depends on the selected node's schema, so
    # every row is mounted by `_rebuild`.  Composing placeholder rows here would
    # collide with the ids `_rebuild` mounts.

    def show(self, node: Node | None, graph: Graph) -> None:
        """Rebuild the form for *node*.

        Re-showing the draft's node re-diffs the draft against the values it now
        stores: after a reload or an undo, a value that reached disk turns clean by
        itself and the others stay (design 1b.8, LLR-004.2, LLR-004.3).
        """
        self.node = node
        self.schema = list(graph.schema)
        if node is not None and node.id == self._draft_node_id:
            self._draft = {f: v for f, v in self._draft.items() if v != self._shown_value(f)}
        if self.is_mounted:
            self.call_next(self._rebuild)

    async def _rebuild(self) -> None:
        screen = self.screen
        focus_was_elsewhere = screen is not None and (
            screen.focused is None or screen.focused not in self.children
        )
        # The chip that held focus is about to be removed.  Its blur also restores the
        # words (measured), but restoring first keeps this independent of Textual
        # posting a blur for a removed widget.
        self._restore_open_words()
        # Removal must be awaited before mounting: Textual only schedules the
        # removal otherwise, so the new rows collide with the outgoing ones on
        # their ids.
        await self.remove_children()
        await self.mount_all(self._rows())
        # Mounting a focusable widget while nothing holds focus makes Textual
        # focus it.  That would hand the keyboard to a text field and silently
        # kill every single-letter map binding.  Only take focus back if it was
        # NOT deliberately somewhere else — otherwise a rebuild triggered by, say,
        # focusing the rail would immediately steal the focus it just granted.
        if self._pending_focus is not None:
            # Focus a field the caller asked for BEFORE these rows existed.
            # Applied here, at the end of the rebuild that created them, so the
            # ordering is causal rather than a race between two scheduled
            # callbacks — which measured 1 pass in 3.
            key, self._pending_focus = self._pending_focus, None
            if self.focus_field(key):
                return
        if screen is not None and focus_was_elsewhere and screen.focused in self.children:
            screen.set_focus(None)

    def _rows(self) -> list:
        if self.node is None:
            return [Static(self._muted("  (select a node)"), id="insp-empty")]

        ficha = self.node.ficha
        node_id = self.node.id
        missing_keys = {f.key for f in ficha.missing_required(self.schema)}
        # The draft overlays what the form shows, so a rebuild never wipes it (A-9).
        draft = self._draft if node_id == self._draft_node_id else {}
        self._labels = {}
        active = STATE_VALUES.index(draft.get("state", self._shown_value("state")))

        rows: list = [
            Static(self._header(ficha), id="insp-header"),
            self._label_row("title", "title"),
            FieldInput(
                value=draft.get("title", darkside.plain(ficha.title)),
                id="insp-title",
                node_id=node_id,
            ),
            self._label_row("state", "state"),
            DsSegmented(STATE_LABELS, active=active, id="insp-state"),
        ]
        for field in self.schema:
            # The row is labelled with the schema's own label, never the key
            # letter — the whole point of LLR-N01.2.
            rows.append(
                self._label_row(
                    field.key, field.label, required_missing=field.key in missing_keys
                )
            )
            rows.append(
                FieldInput(
                    value=draft.get(field.key, darkside.plain(ficha.fields.get(field.key, ""))),
                    id=f"insp-field-{field.key}",
                    node_id=node_id,
                )
            )

        have, req = ficha.required_coverage(self.schema)
        rows += [
            self._label_row("notes", "notes"),
            FieldInput(
                value=draft.get("notes", darkside.plain(ficha.notes)),
                id="insp-notes",
                node_id=node_id,
            ),
            Static(self._label("attachments"), classes="insp-label"),
        ]
        for i, att in enumerate(ficha.attachments):
            # Show the TARGET that would actually be opened, not only the caption:
            # a friendly caption over a hostile path is how a link lies about where
            # it goes (LLR-N02.10).
            rows.append(
                DsChip(
                    label=darkside.plain(f"{att.kind} · {att.caption or att.path}"),
                    id=f"insp-att-{i}",
                    classes="insp-attachment",
                    toggle=False,
                )
            )
            rows.append(
                Static(
                    darkside.Text.assemble(
                        ("   → ", darkside.WORDMARK),
                        (darkside.plain(att.path), darkside.WORDMARK),
                    ),
                    classes="insp-att-target",
                )
            )
        rows.append(
            Static(
                darkside.Text.assemble(("+ add attachment", darkside.ACCENT)),
                id="insp-att-add",
            )
        )
        rows += [
            Static(self._label("coverage"), classes="insp-label"),
            DsProgress(have, max(req, 1), id="insp-coverage"),
        ]
        return rows

    def _header(self, ficha: Ficha) -> darkside.Text:
        header = darkside.Text.assemble(("card", darkside.MUT))
        count = self._dirty_count()
        if count:
            header.append(f"  ● unsaved ({count})", UNSAVED_STYLE)
        header.append("\n")
        header.append(
            darkside.plain(ficha.title or (self.node.id if self.node else "")),
            f"bold {darkside.INK}",
        )
        return header

    def _label(
        self, text: str, *, required_missing: bool = False, dirty: bool = False
    ) -> darkside.Text:
        if required_missing:
            label = darkside.Text.assemble(
                (darkside.plain(text), darkside.ALERT),
                ("  required", darkside.ALERT),
            )
        else:
            label = darkside.Text.assemble((darkside.plain(text), darkside.MUT))
        if dirty:
            label.append("  ●", UNSAVED_STYLE)
        return label

    def _label_row(self, field: str, text: str, *, required_missing: bool = False) -> Static:
        """A field's label, kept by reference so its `●` repaints in place."""
        label = Static(
            self._label(text, required_missing=required_missing, dirty=field in self._shown_draft()),
            classes="insp-label",
        )
        self._labels[field] = (label, text, required_missing)
        return label

    def _shown_draft(self) -> dict[str, str]:
        """The draft entries that belong to the node on show (none for any other)."""
        if self.node is None or self.node.id != self._draft_node_id:
            return {}
        return self._draft

    def _dirty_count(self) -> int:
        return len(self._shown_draft())

    def _paint_dirty(self) -> None:
        """Repaint the header count and the label markers WITHOUT a rebuild.

        A rebuild remounts every row, which would destroy the field being typed
        in on every keystroke (LLR-002.2).
        """
        if self.node is None:
            return
        for header in self.query("#insp-header"):
            header.update(self._header(self.node.ficha))
        draft = self._shown_draft()
        for field, (label, text, required_missing) in self._labels.items():
            label.update(
                self._label(text, required_missing=required_missing, dirty=field in draft)
            )

    # -- the draft (US-001, LLR-001.1, frozen surface I-1) -----------------
    @property
    def draft_node_id(self) -> str | None:
        return self._draft_node_id

    def draft_values(self) -> dict[str, str]:
        """A copy of the dirty entries: mutating it never changes the draft."""
        return dict(self._draft)

    def has_draft(self) -> bool:
        return bool(self._draft)

    def clear_draft(self) -> None:
        self._draft = {}
        self._draft_node_id = None
        self._paint_dirty()

    @staticmethod
    def _field_of(widget) -> str | None:
        """The draft key an inspector input edits, or `None` for any other widget."""
        widget_id = getattr(widget, "id", None) or ""
        if widget_id == "insp-title":
            return "title"
        if widget_id == "insp-notes":
            return "notes"
        if widget_id.startswith("insp-field-"):
            return widget_id[len("insp-field-") :]
        return None

    def _shown_value(self, field: str) -> str:
        """What the form shows for *field* when nothing is drafted (LLR-002.1).

        Dirty is measured against THIS, not against the stored value: a stored
        title that `plain()` alters is shown coerced, and an unknown stored state
        is shown as `ok`, so neither opens dirty.
        """
        ficha = self.node.ficha
        if field == "state":
            return ficha.state if ficha.state in STATE_VALUES else STATE_VALUES[0]
        if field == "title":
            return darkside.plain(ficha.title)
        if field == "notes":
            return darkside.plain(ficha.notes)
        return darkside.plain(ficha.fields.get(field, ""))

    def _put_draft(self, node_id: str | None, field: str, value: str) -> None:
        """Record one field's value in the draft: the one mutator of the draft.

        A change from an input built for another node is stale (the inspector
        re-pointed before it was handled) and is dropped, so it cannot land in
        this node's draft (LLR-001.2).  A value equal to the shown one is not
        dirty, so it leaves the draft.  Also the declared Layer-A test seam (E-3).
        """
        if self.node is None or node_id != self.node.id:
            return
        if value == self._shown_value(field):
            self._draft.pop(field, None)
        else:
            self._draft[field] = value
        # The draft belongs to a node only while it holds something, so
        # `draft_node_id` is `None` exactly when there is no draft.
        self._draft_node_id = node_id if self._draft else None
        self._paint_dirty()

    @staticmethod
    def _muted(text: str) -> darkside.Text:
        return darkside.Text.assemble((darkside.plain(text), darkside.MUT))

    # -- editing -----------------------------------------------------------
    def first_missing_key(self) -> str | None:
        """The schema key of the first required field this node has not filled."""
        if self.node is None:
            return None
        missing = self.node.ficha.missing_required(self.schema)
        return missing[0].key if missing else None

    def focus_after_rebuild(self, key: str | None) -> None:
        """Focus field *key* once the rows for the current node exist."""
        self._pending_focus = key

    def focus_field(self, key: str) -> bool:
        """Put keyboard focus on the input for schema field *key*."""
        try:
            self.query_one(f"#insp-field-{key}", FieldInput).focus()
        except Exception:
            return False
        return True

    # -- attachments (US-N02) ----------------------------------------------
    class AttachmentActivated(Message):
        """The operator asked to open attachment *index* of *node_id*."""

        def __init__(self, node_id: str, index: int) -> None:
            super().__init__()
            self.node_id = node_id
            self.index = index

    class AttachmentAddRequested(Message):
        def __init__(self, node_id: str) -> None:
            super().__init__()
            self.node_id = node_id

    class AttachmentRemoveRequested(Message):
        def __init__(self, node_id: str, index: int) -> None:
            super().__init__()
            self.node_id = node_id
            self.index = index

    def on_ds_chip_changed(self, event: DsChip.Changed) -> None:
        """Activating an attachment chip asks the screen to open it."""
        if self.node is None:
            return
        chip = event.control if hasattr(event, "control") else None
        widget_id = getattr(chip, "id", None) or ""
        if not widget_id.startswith("insp-att-"):
            return
        event.stop()
        try:
            index = int(widget_id[len("insp-att-") :])
        except ValueError:
            return
        self.post_message(self.AttachmentActivated(self.node.id, index))

    # -- the word beside `↵` on a chip (`Z2`) ------------------------------
    # The hint line and the key bar belong to the screen, which writes them from the
    # seat.  This borrows both while a chip has focus and hands back what it found:
    # it only swaps the seat's `open card` for `open attachment` inside text that
    # already carries it, and puts the old text back only if nobody has rewritten it.
    @staticmethod
    def _is_chip(widget) -> bool:
        return (getattr(widget, "id", None) or "").startswith("insp-att-") and isinstance(widget, DsChip)

    def on_descendant_focus(self, event) -> None:
        if self._is_chip(event.widget):
            self._announce_open_attachment()

    def on_descendant_blur(self, event) -> None:
        if self._is_chip(event.widget):
            self._restore_open_words()

    def _announce_open_attachment(self) -> None:
        self._restore_open_words()
        old_pair = hint_pair(SCOPE_MAP, "open_ficha")
        glyph, old_label = old_pair.split(" ", 1)
        saved_hint: str | None = None
        saved_groups: list | None = None
        for line in self.screen.query(HintLine):
            if old_pair in line.text:
                saved_hint = line.text
                line.set_hint(line.text.replace(old_pair, f"{glyph} {ATTACHMENT_OPEN_LABEL}"), line.key)
        for bar in self.screen.query(KeyBar):
            groups = [
                (header, [(g, ATTACHMENT_OPEN_LABEL if (g, word) == (glyph, old_label) else word) for g, word in pairs])
                for header, pairs in bar.groups
            ]
            if groups != bar.groups:
                saved_groups = bar.groups
                bar.set_groups(groups)
        self._chip_override = (saved_hint, saved_groups)

    def _restore_open_words(self) -> None:
        if self._chip_override is None:
            return
        saved_hint, saved_groups = self._chip_override
        self._chip_override = None
        glyph = hint_pair(SCOPE_MAP, "open_ficha").split(" ", 1)[0]
        ours = f"{glyph} {ATTACHMENT_OPEN_LABEL}"
        if saved_hint is not None:
            for line in self.screen.query(HintLine):
                if ours in line.text:
                    line.set_hint(saved_hint, line.key)
        if saved_groups is not None:
            for bar in self.screen.query(KeyBar):
                if any(word == ATTACHMENT_OPEN_LABEL for _, pairs in bar.groups for _, word in pairs):
                    bar.set_groups(saved_groups)

    def request_add_attachment(self) -> None:
        if self.node is not None:
            self.post_message(self.AttachmentAddRequested(self.node.id))

    def request_remove_attachment(self) -> None:
        """Remove the attachment whose chip currently holds focus."""
        if self.node is None or self.screen is None:
            return
        focused = self.screen.focused
        widget_id = getattr(focused, "id", None) or ""
        if not widget_id.startswith("insp-att-"):
            return
        try:
            index = int(widget_id[len("insp-att-") :])
        except ValueError:
            return
        self.post_message(self.AttachmentRemoveRequested(self.node.id, index))

    # Edited IN PLACE, never overridden in a subclass: Textual dispatches every
    # `on_*` handler along the MRO, so a base handler would stay alive (A-8).
    def on_input_changed(self, event: Input.Changed) -> None:
        """Every keystroke updates the draft; nothing is written (LLR-001.2)."""
        field = self._field_of(event.input)
        if field is None:
            return
        event.stop()
        self._put_draft(getattr(event.input, "node_id", None), field, event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """`↵` leaves the field the way `esc` does and keeps the draft (R7, LLR-005.1).

        Run on the INPUT's own queue, not called from here: a message posted while
        this handler runs carries the inspector as its sender, and Textual stops a
        bubbling message at its sender (measured), so `Left` would never reach the
        screen that releases the focus.
        """
        event.stop()
        event.input.call_later(event.input.action_leave_field)

    def on_ds_segmented_changed(self, event: DsSegmented.Changed) -> None:
        """The `state` segment drafts like every other field (R2, LLR-006.1)."""
        if self.node is None:
            return
        event.stop()
        self._put_draft(self.node.id, "state", STATE_VALUES[event.index])
