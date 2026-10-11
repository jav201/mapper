"""The ReqHarness roles screen — matrix variant B (HLR-RH.8, increment RH6a
of batch `2026-10-11-reqharness-batch`; prototype verdict B-123, code-review
follow-up RH6AF pins the paint to `prototypes/roles_screen/proto.py`).

People x roles grid as a Rich `Table` exactly as the prototype's variant B
paints it (`box.SIMPLE_HEAD`, centred cells, `on PANEL` background, `STEP`
header rule), the legend wording copied verbatim from the prototype, and the
footer band as the rounded `Panel`.  There is deliberately NO event ledger
below the matrix: no requirement asks for it and the operator did not adopt
variant C's chain view (prototypes/roles_screen/NOTES.md).

Keys: `j`/`k` move the cursor between people, `h`/`l` between roles, and
`space` PROPOSES the change under the cursor — a grant paints the cell as a
pending add, a revoke as a pending remove, and the proposal lands through the
core's `chain.propose` ONLY (an admin's change about someone else applies in
one event; a change about oneself, or by a non-admin, is written as a pending
request file under `reqharness/pending/` — the screen never edits
`roles.yml`).  With a pending change under the cursor, an admin resolves it:
`a` approves through `chain.approve_pending` (the change lands as the chain
event referencing the request's sha256) and `r` rejects through
`chain.reject_pending` (an empty `resolution` event) — the screen never
writes roles.yml itself and never resolves its own request (the core
refuses; the named refusal is painted).  The action re-reads disk first (the
core stays the authority at keypress time); with SEVERAL open requests on
one cell it refuses with the named hint instead of silently picking the
oldest (resolution is core-only, B-126 follow-up).  The band carries the chain event
count, the head hash (truncated to 12 hex + the ellipsis), the viewer
identity, the pending detail (capped to one line), the chain status and the
release verdict.  A tampered or forked chain makes the matrix read-only:
`space`, `a` and `r` are inert and the hint says why (R14).  Fork recovery
is core-only (B-126).

Width (RH6AF ruling): at 87 columns with 6+ roles or ids over 12 chars the
grid must not wrap, so person ids are truncated with the ellipsis at a fixed
12-cell column (a Rich `Table` accepts `Text` cells with `no_wrap` — chosen
over a scroll container because it keeps the table exactly the shape the
prototype paints at 87); when the natural grid exceeds the width the role
columns shrink uniformly and their headers truncate with the ellipsis.

Repo discovery is D13: `git rev-parse --show-toplevel` over the app's
workspace; a `safe.directory` refusal or any git failure lands on the named
`no repo` result — the screen says so and offers nothing to edit.

Every file-derived string (person ids, names, roles, notes, hashes, status
words) passes through `darkside.plain` and is painted ONLY into
`rich.text.Text` sinks (R10): table cells, headers, legend and band lines are
`Text` objects — never `Static(str)`, never markup.  All colours are
darkside tokens; the cell glyphs below are the one sanctioned matrix set of
LLR-RH.8.1 (census-enforced in `tests/test_roles_screen.py`).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from rich import box
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static

from mapper import darkside
from mapper.keymap import SCOPE_ROLES, groups_for_keybar, hint_pair
from mapper.reqharness import chain, identity, pending as pending_mod, release
from mapper.reqharness.config import email_sha256, load_config
from mapper.reqharness.records import Config, Person, ValidationError
from mapper.screens.common import keybar_groups, screen_bindings
from mapper.widgets.chrome import HintLine, KeyBar, TabStrip

#: The matrix cell glyph set — LLR-RH.8.1's sanctioned four, declared once so
#: the census has exactly one place to guard (no other glyph literal may
#: appear in this module).
GLYPH_IN_FORCE = "\u25cf"       # ● role held, per the verified chain prefix
GLYPH_PENDING_ADD = "\u25d0"    # ◐ a grant waits on an admin's approval
GLYPH_PENDING_REMOVE = "\u25cc"  # ◌ a revoke waits on an admin's approval
GLYPH_NOT_HELD = "\u25cb"       # ○ role not held

#: What the operator reads while the matrix cannot be edited (R14).  The
#: status word is appended verbatim — it is a core status word, never prose.
_READ_ONLY_HINT = "roles are read-only \u2014 {} \u00b7 space does nothing"
_NO_REPO_HINT = "no repo \u2014 connect a repository before editing roles"
_NOT_DECLARED_HINT = (
    "your git identity matches no declared person \u2014 space proposes nothing"
)
_PENDING_ALREADY_HINT = "that change is already pending"
_PROPOSED_HINT = "proposed \u2014 recorded as a pending request for an admin"
_APPLIED_HINT = "applied \u2014 one approved chain event"
#: LLR-RH.8.6: the non-admin refusal is byte-exact per R6.
_NOT_ADMIN_KEY_HINT = "{} is unavailable (needs an admin)"
_NO_PENDING_HINT = "no pending change under the cursor"
#: RHFIX6B: with SEVERAL open requests on one cell the screen must not
#: silently pick the oldest — resolution is core-only (B-126 follow-up).
_SEVERAL_PENDING_HINT = (
    "several pending requests on this cell \u2014 "
    "resolve them from the core (B-126 follow-up)"
)

_NO_REPO = "no repo"

#: The person-id column cap, in display cells — ids truncate with the
#: ellipsis at this width so the grid never wraps at 87 columns (RH6AF).
_ID_CAP = 12
#: The head-hash cap: 12 hex cells + the ellipsis (RH6AF).
_HEAD_CAP = 12
#: The band's fixed chrome: panel border (2) + panel padding (2).
_BAND_CHROME = 4
#: The band's fixed height: 2 border + 3 content lines (pending, chain,
#: verdict) — fixed in `RolesScreen.CSS` so the band never reflows.
_BAND_HEIGHT = 5


@dataclass
class _Snapshot:
    """Everything the screen paints, loaded from the core on (re)load.

    `root is None` is the named `no repo` state; `config_error` names a
    config refusal (R9) and paints no matrix; `read_only` is derived — the
    matrix is editable only while the chain verifies.
    """

    root: Path | None = None
    status: str = _NO_REPO
    events: tuple = ()
    people: tuple[Person, ...] = ()
    roles: tuple[str, ...] = ()
    held: dict[str, frozenset] = field(default_factory=dict)
    pending_adds: dict[str, frozenset] = field(default_factory=dict)
    pending_removes: dict[str, frozenset] = field(default_factory=dict)
    pending_names: tuple[str, ...] = ()  # file-derived, display-ready
    open_requests: tuple = ()  # the pending-derived open PendingRequests
    viewer_id: str = ""
    viewer_known: bool = False
    viewer_admin: bool = False
    verdict: str = "not ready \u00b7 no repo"
    config_error: str = ""

    @property
    def read_only(self) -> bool:
        """R14: the matrix is editable only in the verified state."""
        return self.status != chain.STATUS_VERIFIED


# ---------------------------------------------------------------------------
# Loading — the screen reads the core and paints; it writes ONLY through
# `chain.propose` (the core's one write path enforces the chain rules).
# ---------------------------------------------------------------------------


def _verdict(root: Path, report: chain.ChainReport, config: Config) -> str:
    """The release verdict word (LLR-RH.8.3), derived exactly as `audit.audit`
    derives it, with the one tolerance a screen owes: a registry whose canon
    (`REQUIREMENTS.md`) does not exist yet is not an error here — the verdict
    is evaluated over an empty canon, and the missing file is not named on
    this surface (it is named on `--audit`)."""
    if not report.ok:
        return release.VERDICT_NOT_VERIFIABLE
    from mapper.reqharness.cache import ParseCache
    from mapper.reqharness.derive import derive_states, load_canon
    from mapper.reqharness.reviews import load_reviews

    scan = load_reviews(root, cache=ParseCache.disabled())
    try:
        canon, _reported = load_canon(root)
    except ValidationError:
        canon = ()
    derivation = derive_states(canon, scan, report, config)
    return release.evaluate(config, report, derivation).text


def _load(workspace: Path) -> _Snapshot:
    """One pass over the core: discover the repo (D13), verify the chain,
    fold the verified prefix, scan the pending store, read the viewer
    identity.  Every degradation is a named state, never a crash."""
    snap = _Snapshot()
    top = identity.repo_root(workspace)
    if top == identity.NO_REPO:
        return snap
    root = Path(top)
    snap.root = root
    report = release.safe_verify(root)
    snap.status = report.status
    snap.events = report.events
    try:
        config = load_config(root)
    except ValidationError as exc:
        # A config refusal is named on screen (R9); the matrix is not painted.
        snap.config_error = darkside.plain(str(exc))
        snap.verdict = release.VERDICT_NOT_VERIFIABLE
        return snap
    snap.people = config.people
    snap.roles = config.roles
    if report.events:
        snap.held = {
            person: frozenset(roles)
            for person, roles in chain.effective_roles(report).items()
        }
    scan = pending_mod.list_pending(root)
    open_requests = [
        request
        for request in scan.requests
        if pending_mod.resolution(report, request) == pending_mod.RESOLVED_PENDING
    ]
    snap.open_requests = tuple(
        sorted(open_requests, key=lambda r: (r.time, r.name))
    )
    adds: dict[str, set[str]] = {}
    removes: dict[str, set[str]] = {}
    names: list[str] = []
    for request in snap.open_requests:
        glyph = "+" if request.action == "grant" else "-"
        names.append(
            f"{request.person} {glyph}{request.role} by {request.requested_by}"
        )
        target = adds if request.action == "grant" else removes
        target.setdefault(request.person, set()).add(request.role)
    snap.pending_adds = {k: frozenset(v) for k, v in adds.items()}
    snap.pending_removes = {k: frozenset(v) for k, v in removes.items()}
    snap.pending_names = tuple(names)
    who = identity.read(root)
    viewer = next(
        (
            person
            for person in config.people
            if person.email_sha256 == email_sha256(who.email)
        ),
        None,
    )
    if viewer is not None:
        snap.viewer_id = viewer.id
        snap.viewer_known = True
        snap.viewer_admin = "admin" in snap.held.get(viewer.id, ())
    elif who.name or who.email:
        snap.viewer_id = who.name or who.email
    snap.verdict = _verdict(root, report, config)
    return snap


# ---------------------------------------------------------------------------
# Painting — Text sinks only (R10); darkside tokens only; file-derived text
# coerced through darkside.plain first.  The shapes are the prototype's
# variant B: a Rich `Table` (SIMPLE_HEAD, centred cells, panel background),
# the legend copied verbatim, and the footer band as a rounded `Panel`.
# ---------------------------------------------------------------------------


def _chain_word(snap: _Snapshot) -> tuple[str, str]:
    """The chip word + colour, per LLR-RH.8.3's exact status text: the
    verified chain paints `✓ verified`; a tampered or forked chain paints the
    core status word verbatim (`config changed without approval`, `chain
    forked at seq N`)."""
    ok = snap.status == chain.STATUS_VERIFIED
    if ok:
        return "\u2713 verified", darkside.SAGE
    return darkside.plain(snap.status), darkside.ALERT


def _viewer_text(snap: _Snapshot, ok: bool) -> Text:
    """The viewer identity piece shared by the status line and the band."""
    style = darkside.MUT if ok else darkside.WARN
    if snap.viewer_known:
        if snap.viewer_admin:
            return Text.assemble(
                (darkside.plain(snap.viewer_id), darkside.INK),
                (" (admin)", style),
            )
        return Text.assemble(
            (darkside.plain(snap.viewer_id), darkside.INK),
            (" \u2014 not admin: proposals become requests", style),
        )
    if snap.viewer_id:
        return Text.assemble(
            (darkside.plain(snap.viewer_id), darkside.INK),
            (" \u2014 no declared person", darkside.WARN),
        )
    return Text("")


def _cap_line(text: Text, width: int) -> Text:
    """One line, hard-capped at `width` cells with the ellipsis — a capped
    line can never wrap, so the band's fixed height holds at 87 columns."""
    text.truncate(max(width, 1), overflow="ellipsis")
    return text


def _status_text(snap: _Snapshot, width: int) -> Text:
    """The chain chip + status word + viewer identity (the prototype's
    `_chain_status` line)."""
    if snap.root is None:
        return Text.assemble(
            (" chain ", f"bold {darkside.GROUND} on {darkside.ALERT}"),
            (f" {_NO_REPO}", darkside.ALERT),
        )
    word, colour = _chain_word(snap)
    status = Text.assemble(
        (" chain ", f"bold {darkside.GROUND} on {colour}"),
        (f" {word}", colour),
    )
    viewer = _viewer_text(snap, colour == darkside.SAGE)
    if viewer.plain:
        status.append("  viewer ", darkside.MUT)
        status.append_text(viewer)
    return _cap_line(status, width)


def _matrix_renderable(snap: _Snapshot, row: int, col: int, width: int):
    """The people x roles `Table` + the prototype's legend + the verbatim
    genesis copy (LLR-RH.8.1).  No event ledger — variant C's chain view was
    never adopted (NOTES.md)."""
    if snap.root is None or snap.config_error:
        # The named degradation paints once — no ledger below repeats it.
        message = _NO_REPO_HINT if snap.root is None else snap.config_error
        return Text(darkside.plain(message), style=darkside.WARN)
    ids = [darkside.plain(person.id) for person in snap.people]
    roles = [darkside.plain(role) for role in snap.roles]
    name_w = min(max([darkside.shown_cells(i) for i in ids] + [6]), _ID_CAP)
    table = Table(box=box.SIMPLE_HEAD, header_style=f"bold {darkside.MUT}",
                  style=f"on {darkside.PANEL}", expand=True,
                  border_style=darkside.STEP, pad_edge=False)
    table.add_column(Text("person"), style=f"bold {darkside.INK}",
                     width=name_w + 2, no_wrap=True)
    # Never wrap: ids cap at _ID_CAP above; when the natural grid (2 cells of
    # horizontal padding per column) would exceed the width, the role columns
    # shrink uniformly and their headers truncate with the ellipsis.
    natural = name_w + 2 + sum(max(3, darkside.shown_cells(r)) + 2 for r in roles)
    if roles and natural > width - 2:
        role_w = max(5, (width - 2 - (name_w + 2)) // len(roles))
    else:
        role_w = 0
    for role in roles:
        header = Text(darkside.fit(role, role_w - 2)) if role_w else Text(role)
        if role_w:
            table.add_column(header, justify="center", style=darkside.ASH,
                             width=role_w, no_wrap=True)
        else:
            table.add_column(header, justify="center", style=darkside.ASH,
                             no_wrap=True)
    for i, person in enumerate(ids):
        display = person
        if darkside.shown_cells(person) > name_w:
            display = darkside.fit(person, name_w)
        if i == row:
            name_cell = Text.assemble(
                ("\u25b8 ", f"bold {darkside.INK}"),
                (display, f"bold {darkside.INK}"))
        else:
            name_cell = Text(display)
        cells = []
        for j, role in enumerate(roles):
            held_role = role in snap.held.get(person, frozenset())
            if role in snap.pending_adds.get(person, frozenset()):
                glyph, colour = GLYPH_PENDING_ADD, darkside.WARN
            elif role in snap.pending_removes.get(person, frozenset()):
                glyph, colour = GLYPH_PENDING_REMOVE, darkside.WARN
            elif held_role:
                glyph, colour = GLYPH_IN_FORCE, darkside.SAGE
            else:
                glyph, colour = GLYPH_NOT_HELD, darkside.WORDMARK
            if i == row and j == col:
                cells.append(Text(f" {glyph} ",
                                  style=f"bold {darkside.GROUND} on {darkside.ACCENT}"))
            else:
                cells.append(Text(f" {glyph} ", style=colour))
        table.add_row(name_cell, *cells)
    # The legend wording is the prototype's, verbatim.
    legend = Text.assemble(
        (f" {GLYPH_IN_FORCE} ", darkside.SAGE), ("in force   ", darkside.MUT),
        (f" {GLYPH_PENDING_ADD} ", darkside.WARN), ("pending toggle   ", darkside.MUT),
        (f" {GLYPH_NOT_HELD} ", darkside.WORDMARK), ("not held   ", darkside.MUT),
        ("space", darkside.ACCENT), (" on a cell proposes the change", darkside.MUT),
    )
    parts: list = [table, legend]
    genesis = next((e for e in snap.events if e.action == "genesis"), None)
    if genesis is not None:
        parts.append(Text(f"genesis \u2014 {darkside.plain(genesis.note)}",
                          style=darkside.MUT))
    return Group(*parts)


def _band_renderable(snap: _Snapshot, width: int) -> Panel:
    """The footer band (LLR-RH.8.3) as the prototype's rounded `Panel`: the
    pending detail (capped to one line, overflow as `… +N more`), the chain
    status + event count + truncated head hash + viewer, and the release
    verdict — in every state, at a fixed height."""
    inner = max(20, width - _BAND_CHROME)
    if snap.root is None:
        return Panel(Text.assemble(
            (f"{_NO_REPO} \u00b7 ", darkside.ALERT),
            (darkside.plain(snap.verdict), darkside.WARN),
        ), box=box.ROUNDED, border_style=darkside.STEP,
           style=f"on {darkside.PANEL}")
    head = (darkside.plain(snap.events[-1].this_hash)[:_HEAD_CAP] + "\u2026"
            if snap.events else "\u2014")
    word, colour = _chain_word(snap)
    if snap.pending_names:
        count = len(snap.pending_names)
        extra = f"  \u2026 +{count - 1} more" if count > 1 else ""
        tail = "  awaiting admin approval"
        prefix = f"pending ({count}): "
        budget = max(8, inner - darkside.shown_cells(prefix)
                     - darkside.shown_cells(tail) - darkside.shown_cells(extra))
        newest = darkside.fit(darkside.plain(snap.pending_names[-1]),
                              budget).rstrip()
        pending = Text.assemble(
            (prefix, f"bold {darkside.WARN}"), (newest, darkside.INK),
            (tail, darkside.WARN), (extra, darkside.MUT),
        )
    else:
        pending = Text("pending 0", darkside.MUT)
    chain_line = Text.assemble(
        (word, colour), (" \u00b7 ", darkside.MUT),
        (f"{len(snap.events)} event{'s' if len(snap.events) != 1 else ''}",
         darkside.INK),
        (" \u00b7 ", darkside.MUT), ("head ", darkside.MUT), (head, darkside.INK),
        (" \u00b7 ", darkside.MUT), ("viewer ", darkside.MUT),
        _viewer_text(snap, colour == darkside.SAGE),
    )
    verdict = Text.assemble(
        ("release ", darkside.MUT),
        (darkside.plain(snap.verdict),
         darkside.SAGE if snap.verdict == release.VERDICT_READY else darkside.WARN),
    )
    return Panel(Group(pending, _cap_line(chain_line, inner), verdict),
                 box=box.ROUNDED, border_style=darkside.STEP,
                 style=f"on {darkside.PANEL}")


def _hint(snap: _Snapshot) -> str:
    """The hint line: the seat's word beside `space` (K3), truthful per state."""
    propose = hint_pair(SCOPE_ROLES, "propose")
    if snap.root is None:
        return _NO_REPO_HINT
    if snap.config_error:
        return "config refused \u2014 the matrix cannot be painted"
    if snap.read_only:
        return _READ_ONLY_HINT.format(darkside.plain(snap.status))
    if not snap.viewer_known:
        return _NOT_DECLARED_HINT
    if snap.viewer_admin:
        return (f"{propose} \u2014 as admin, a change to someone else applies now; "
                "your own changes pend")
    return f"{propose} \u2014 you are not an admin: proposals become pending requests"


class RolesScreen(Screen):
    """The ReqHarness roles screen — matrix variant B (B-123, RH6AF paint)."""

    KEY_SCOPE = SCOPE_ROLES
    BINDINGS = screen_bindings(SCOPE_ROLES)

    CSS = f"""
    #roles-band {{ height: {_BAND_HEIGHT}; }}
    """

    def __init__(self) -> None:
        super().__init__()
        self._snap = _Snapshot()
        self._row = 0
        self._col = 0

    def compose(self) -> ComposeResult:
        yield TabStrip(None, crumb=["home", "roles"])
        yield Static(id="roles-status")
        yield Static(id="roles-body")
        yield Static(id="roles-band")
        yield HintLine("")
        yield KeyBar(groups_for_keybar(keybar_groups(self.KEY_SCOPE)))

    def on_mount(self) -> None:
        self._reload()

    def on_screen_resume(self) -> None:
        """A resolution made elsewhere (another screen, a manual act) is
        re-read, never assumed."""
        self._reload()

    # -- loading / painting --------------------------------------------------

    def _reload(self) -> None:
        workspace = Path(self.app.store.workspace)  # type: ignore[attr-defined]
        self._snap = _load(workspace)
        self._paint()

    def _paint(self) -> None:
        snap = self._snap
        self._row = self._clamp_row(self._row)
        self._col = self._clamp_col(self._col)
        width = self.app.console.width
        self.query_one("#roles-status", Static).update(_status_text(snap, width))
        self.query_one("#roles-body", Static).update(
            _matrix_renderable(snap, self._row, self._col, width))
        self.query_one("#roles-band", Static).update(_band_renderable(snap, width))
        self.query_one(HintLine).set_hint(_hint(snap))

    def _clamp_row(self, row: int) -> int:
        count = max(1, len(self._snap.people))
        return row % count

    def _clamp_col(self, col: int) -> int:
        count = max(1, len(self._snap.roles))
        return col % count

    # -- cursor ---------------------------------------------------------------

    def action_next_person(self) -> None:
        self._row = self._clamp_row(self._row + 1)
        self._paint()

    def action_prev_person(self) -> None:
        self._row = self._clamp_row(self._row - 1)
        self._paint()

    def action_next_role(self) -> None:
        self._col = self._clamp_col(self._col + 1)
        self._paint()

    def action_prev_role(self) -> None:
        self._col = self._clamp_col(self._col - 1)
        self._paint()

    # -- proposing (the only write, and it goes through the core) --------------

    def action_propose(self) -> None:
        snap = self._snap
        hint = self.query_one(HintLine)
        if snap.root is None or snap.config_error or snap.read_only:
            hint.set_hint(_hint(snap))  # R14: inert, and the message says why
            return
        if not snap.viewer_known:
            hint.set_hint(_NOT_DECLARED_HINT)
            return
        person = snap.people[self._row]
        role = snap.roles[self._col]
        if (role in snap.pending_adds.get(person.id, frozenset())
                or role in snap.pending_removes.get(person.id, frozenset())):
            hint.set_hint(_PENDING_ALREADY_HINT)
            return
        action = "revoke" if role in snap.held.get(person.id, frozenset()) else "grant"
        try:
            pending_path = chain.propose(
                snap.root, requester=snap.viewer_id, action=action,
                person=person.id, role=role,
            )
        except ValidationError as exc:
            # `INC9-SEC-F1`: the exception TYPE only, never `str(exc)` — a
            # toast may not paint a path the core's refusal text could embed.
            self.notify(
                darkside.plain(
                    f"could not propose the change: {type(exc).__name__}"),
                severity="error", markup=False)
            return
        except OSError as exc:
            # A writer failure (disk full, permissions, a vanished directory)
            # is named by TYPE only, under the same rule: the message may not
            # paint whatever path or detail the OS error text could embed.
            self.notify(
                darkside.plain(
                    f"could not propose the change: {type(exc).__name__}"),
                severity="error", markup=False)
            return
        self._reload()
        self.query_one(HintLine).set_hint(
            _PROPOSED_HINT if pending_path is not None else _APPLIED_HINT)

    # -- resolving a pending request (admin only, through the core only) -------

    def action_approve(self) -> None:
        self._resolve_pending(approve=True)

    def action_reject(self) -> None:
        self._resolve_pending(approve=False)

    def _resolve_pending(self, *, approve: bool) -> None:
        """LLR-RH.8.6: `a`/`r` resolve the pending change under the cursor
        through `chain.approve_pending` / `chain.reject_pending` — the screen
        never writes roles.yml and never reaches the core with a key that has
        no business resolving (non-admin, read-only, nothing pending).  The
        core's own refusals (own request, already resolved) are painted
        VERBATIM — they are the named refusal, and R22 names files by name;
        an `OSError` is named by TYPE only, under the propose path's rule
        (the OS error text could embed a path).

        RHFIX6B: the action RELOADS first — the core stays the authority, so
        the admin pre-filter and the selected request reflect DISK at
        keypress time, not the mount-time snapshot.  With several open
        requests on one cell the action refuses with the named hint instead
        of silently picking the oldest (resolution is core-only, B-126
        follow-up).  A success names the request it resolved."""
        self._reload()  # the core is the authority: read disk at keypress time
        snap = self._snap
        hint = self.query_one(HintLine)
        key = "a" if approve else "r"
        if snap.root is None or snap.config_error or snap.read_only:
            hint.set_hint(_hint(snap))  # R14: inert, and the message says why
            return
        if not snap.viewer_admin:
            hint.set_hint(_NOT_ADMIN_KEY_HINT.format(key))
            return
        person = snap.people[self._row]
        role = snap.roles[self._col]
        matching = [
            item
            for item in snap.open_requests
            if item.person == person.id and item.role == role
        ]
        if not matching:
            hint.set_hint(_NO_PENDING_HINT)
            return
        if len(matching) > 1:
            hint.set_hint(_SEVERAL_PENDING_HINT)
            return
        request = matching[0]
        resolve = chain.approve_pending if approve else chain.reject_pending
        try:
            resolve(snap.root, pending=request.name, approver=snap.viewer_id)
        except ValidationError as exc:
            # The named refusal lands on the HINT LINE verbatim (a Text sink —
            # `darkside.hint_line` coerces through `plain()`): the core's
            # resolution refusals name the rule, never a workspace path.  The
            # toast stays TYPE-only, under the propose path's `INC9-SEC-F1`
            # rule (a toast may not paint text an exception could embed).
            hint.set_hint(darkside.plain(str(exc)))
            verb = "approve" if approve else "reject"
            self.notify(
                darkside.plain(
                    f"could not {verb} the request: {type(exc).__name__}"),
                severity="error", markup=False)
            return
        except OSError as exc:
            verb = "approve" if approve else "reject"
            self.notify(
                darkside.plain(
                    f"could not {verb} the request: {type(exc).__name__}"),
                severity="error", markup=False)
            return
        self._reload()
        sign = "+" if request.action == "grant" else "-"
        verb = "approved" if approve else "rejected"
        # The success names the resolved request; every file-derived part is
        # coerced through `darkside.plain`.  `set_hint` paints through
        # `darkside.hint_line`, a `Text` sink that never parses markup.
        hint.set_hint(
            f"{verb}: {darkside.plain(request.person)} "
            f"{sign}{darkside.plain(request.role)} "
            f"(requested by {darkside.plain(request.requested_by)})")

    def action_home(self) -> None:
        self.app.pop_screen()
