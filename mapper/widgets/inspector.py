"""The editable ficha inspector — variant A «taller»'s right-hand panel.

This widget owns no persistence.  `docs/ARCHITECTURE.md` §3 bans `widgets → store`,
so an edit here is posted as a message and the owning screen — which holds the
graph and the store — decides what to write.  That keeps the whole-graph write on
the one object entitled to make it.

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
from mapper.model import Ficha, Graph, Node, SchemaField
from mapper.widgets.components import DsChip, DsProgress, DsSegmented

# The four states a ficha may carry, and the Spanish words shown for them.
STATE_VALUES = ["ok", "risk", "late", "blocked"]
STATE_LABELS = ["ok", "riesgo", "tarde", "bloq"]

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
    """

    BINDINGS = [Binding("escape", "leave_field", "salir del campo")]

    class Left(Message):
        """The operator stepped out of a field without abandoning the value."""

    def action_leave_field(self) -> None:
        self.post_message(self.Left())


class FichaInspector(Vertical):
    """Editable form for the selected node's ficha."""

    class FieldCommitted(Message):
        """A ficha value was committed and the screen should persist it.

        `field` is a schema key, or one of the pseudo-keys `title` / `notes` /
        `state`, which live on the `Ficha` itself rather than in `fields`.
        """

        def __init__(self, node_id: str, field: str, value: str) -> None:
            super().__init__()
            self.node_id = node_id
            self.field = field
            self.value = value

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.node: Node | None = None
        self.schema: list[SchemaField] = []

    # -- rendering ---------------------------------------------------------
    # No `compose`: the form's shape depends on the selected node's schema, so
    # every row is mounted by `_rebuild`.  Composing placeholder rows here would
    # collide with the ids `_rebuild` mounts.

    def show(self, node: Node | None, graph: Graph) -> None:
        """Rebuild the form for *node*."""
        self.node = node
        self.schema = list(graph.schema)
        if self.is_mounted:
            self.call_next(self._rebuild)

    async def _rebuild(self) -> None:
        screen = self.screen
        focus_was_elsewhere = screen is not None and (
            screen.focused is None or screen.focused not in self.children
        )
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
        if screen is not None and focus_was_elsewhere and screen.focused in self.children:
            screen.set_focus(None)

    def _rows(self) -> list:
        if self.node is None:
            return [Static(self._muted("  (selecciona un nodo)"), id="insp-empty")]

        ficha = self.node.ficha
        missing_keys = {f.key for f in ficha.missing_required(self.schema)}
        active = STATE_VALUES.index(ficha.state) if ficha.state in STATE_VALUES else 0

        rows: list = [
            Static(self._header(ficha), id="insp-header"),
            Static(self._label("título"), classes="insp-label"),
            FieldInput(value=darkside.plain(ficha.title), id="insp-title"),
            Static(self._label("estado"), classes="insp-label"),
            DsSegmented(STATE_LABELS, active=active, id="insp-state"),
        ]
        for field in self.schema:
            # The row is labelled with the schema's own label, never the key
            # letter — the whole point of LLR-N01.2.
            rows.append(
                Static(
                    self._label(field.label, required_missing=field.key in missing_keys),
                    classes="insp-label",
                )
            )
            rows.append(
                FieldInput(
                    value=darkside.plain(ficha.fields.get(field.key, "")),
                    id=f"insp-field-{field.key}",
                )
            )

        have, req = ficha.required_coverage(self.schema)
        rows += [
            Static(self._label("notas"), classes="insp-label"),
            FieldInput(value=darkside.plain(ficha.notes), id="insp-notes"),
            Static(self._label("adjuntos"), classes="insp-label"),
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
                darkside.Text.assemble(("+ agregar adjunto", darkside.ACCENT)),
                id="insp-att-add",
            )
        )
        rows += [
            Static(self._label("cobertura"), classes="insp-label"),
            DsProgress(have, max(req, 1), id="insp-coverage"),
        ]
        return rows

    def _header(self, ficha: Ficha) -> darkside.Text:
        return darkside.Text.assemble(
            ("ficha\n", darkside.MUT),
            (darkside.plain(ficha.title or (self.node.id if self.node else "")),
             f"bold {darkside.INK}"),
        )

    def _label(self, text: str, *, required_missing: bool = False) -> darkside.Text:
        if required_missing:
            return darkside.Text.assemble(
                (darkside.plain(text), darkside.ALERT),
                ("  requerido", darkside.ALERT),
            )
        return darkside.Text.assemble((darkside.plain(text), darkside.MUT))

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

    def on_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self._commit(event.input)

    def on_input_blurred(self, event: Input.Blurred) -> None:
        self._commit(event.input)

    def _commit(self, widget: Input) -> None:
        if self.node is None or not widget.id:
            return
        if widget.id == "insp-title":
            field = "title"
        elif widget.id == "insp-notes":
            field = "notes"
        elif widget.id.startswith("insp-field-"):
            field = widget.id[len("insp-field-") :]
        else:
            return
        self.post_message(self.FieldCommitted(self.node.id, field, widget.value))

    def on_ds_segmented_changed(self, event: DsSegmented.Changed) -> None:
        if self.node is None:
            return
        event.stop()
        self.post_message(
            self.FieldCommitted(self.node.id, "state", STATE_VALUES[event.index])
        )
