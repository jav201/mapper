"""The ReqHarness REVIEW / SIGNING screen — variant A (list + detail) with the
"needs action" filter preset, two-key confirmed signing, a fixed bottom release
band and the informative-change badge (B-134, HLR-RS.1..5 / LLR-RS.1.* / LLR-RS.2.*).

The prototype verdict (`prototypes/review_screen/NOTES.md`, variant A) fixed the
look this screen ports: a filterable object table (object · derived state · last
review) beside a detail pane (who reviewed what at which head, digest ✓/✗,
unentitled reviews apart, the `⁂ changed (informative)` mark explained), the
"needs action" filter preset over the open states, and a fixed release band at
the bottom (mandatory rules + the exact verdict text from `release.evaluate`).

Signing is TWO-KEY (`b` arms, `enter` confirms) and writes ONLY through the
headless `signing.sign_review` orchestration — the screen never writes a review
file itself.  `b` captures a sign intent from the one worker snapshot (object id,
normative digest, current head) and paints it on the hint line in the ACCENT
token; `enter` disarms on the UI thread first (F5), then starts ONE sign worker
which re-reads the identity and re-verifies the chain inside itself (A7) before
calling `sign_review`.  At most one sign is in flight; `b`/`enter` are inert
while it runs; while armed, ANY key other than `enter` (including `escape` and
`q`) cancels the arm and stays; `q`/`escape` leave (home) only when not armed.
Refusals paint on the hint line in the roles-screen ALERT/WARN token; the armed
hint and the armed row use ACCENT.  The `ReviewList` is a line-based `ScrollView`
with a `render_line` method that binds NO keys; the screen owns `enter`.

ALL disk/git work runs in one thread worker (the `roles.py` pattern): identity
repo-root + identity read, `verify_chain`, `load_config`, `load_canon`,
`load_reviews`, `derive.derive_states` and `release.evaluate` return ONE
immutable snapshot, applied on the UI thread in `on_worker_state_changed` only
when the worker state is SUCCESS and after the generation + `is_attached` checks.
Until the first snapshot the keys (up, down, 4, b, enter) are inert and the key
bar advertises only `escape`.  A tampered, forked or no-registry result paints
the read-only state with its reason and makes `b` inert (hidden from the key
bar).  Every file-derived string passes through `darkside.plain` into
`rich.text.Text` sinks (R10 / C8); colours come from `darkside` tokens, keys from
the seat, and no string outside the §6.6 copy table plus the approved-prototype
set is painted (U4).
"""
from __future__ import annotations

import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from rich import box
from rich.cells import cell_len
from rich.console import Group
from rich.panel import Panel
from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.geometry import Size
from textual.screen import Screen
from textual.scroll_view import ScrollView
from textual.strip import Strip
from textual.widgets import Static
from textual.worker import WorkerState

from mapper import darkside
from mapper.keymap import SCOPE_REVIEW, group_header, groups_for_keybar
from mapper.reqharness import chain, derive, identity, release, reviews, signing
from mapper.reqharness.audit import NO_REGISTRY, VERDICT_NO_REGISTRY
from mapper.reqharness.config import REQHARNESS_DIR, email_sha256, load_config
from mapper.reqharness.records import (
    REASON_AUTHOR,
    REASON_NO_ROLE,
    SigningRefused,
    ValidationError,
)
from mapper.screens.common import keybar_groups, screen_bindings
from mapper.widgets.chrome import HintLine, KeyBar, TabStrip

# ---------------------------------------------------------------------------
# The §6.6 copy table (the ONLY new UI strings this screen may paint) and the
# approved-prototype words it reuses.  The dynamic `<...>` placeholders are
# filled from the snapshot; a long `<object>`/`<viewer>` elides its MIDDLE (U1).
# ---------------------------------------------------------------------------

_SIGN_ARMED_HEAD = "sign "
_SIGN_ARMED_DIGEST = " \u00b7 digest "
_SIGN_ARMED_HEADWORD = " \u00b7 head "
_SIGN_ARMED_TAIL = " \u2014 enter confirms, any other key cancels"

_REFUSE_CHAIN = "cannot sign: registry not verifiable ({status})"
_REFUSE_VIEWER = "cannot sign: {viewer} is not a declared person"
_REFUSE_AMBIGUOUS = "cannot sign: several people match your git identity \u2014 declare exactly one"
_REFUSE_NO_ROLE = "cannot sign: {viewer} does not hold the {role} role at this head"
_REFUSE_OBJECT = "cannot sign: unknown object {object}"
_REFUSE_RETIRED = "cannot sign: {object} is retired"
_REFUSE_CLASS = "cannot sign: {object}'s class is not declared"
_REFUSE_AUTHOR = "cannot sign: {viewer} authored this object's batch"
_REFUSE_MOVED = "cannot sign: something changed since b (object, content, head or role) \u2014 press b to re-arm"
_REFUSE_DUP = "cannot sign: this content was already signed"
_REFUSE_LIMIT = "cannot sign: the review-file limit is reached"

_EMPTY_CANON = "no canon objects"
_EMPTY_HISTORY = "no review event names this id"
_KEYBAR_ARMED = "enter sign \u00b7 any other key cancel"

_READ_ONLY_HINT = "registry not verifiable \u2014 b signs nothing"
_REST_HINT = "viewer {viewer} ({roles}) \u2014 b signs only what your role covers"

# The hint line's own chrome ("next ▸ ") so the elision budget is exact.
_HINT_PREFIX_CELLS = darkside.shown_cells("next \u25b8 ")

#: The band's fixed height (2 border + 5 rule rows + 1 verdict row).
_BAND_HEIGHT = 8

_STATE_ORDER = (
    derive.STATE_REVIEWED,
    derive.STATE_CHANGED,
    derive.STATE_PRE_REVIEWED,
    derive.STATE_NOT_REVIEWED,
    derive.STATE_RETIRED,
)
_STATE_STYLE = {
    derive.STATE_REVIEWED: darkside.SAGE,
    derive.STATE_CHANGED: darkside.WARN,
    derive.STATE_PRE_REVIEWED: darkside.ACCENT,
    derive.STATE_NOT_REVIEWED: darkside.ASH,
    derive.STATE_RETIRED: darkside.MUT,
}

#: The filter cycle, "needs action" = the open states (variant C's queue).
_FILTER_NEEDS_ACTION = "needs action"
_FILTERS = (
    "all",
    _FILTER_NEEDS_ACTION,
    derive.STATE_REVIEWED,
    derive.STATE_CHANGED,
    derive.STATE_PRE_REVIEWED,
    derive.STATE_NOT_REVIEWED,
    derive.STATE_RETIRED,
)
_NEEDS_ACTION_STATES = frozenset(
    {derive.STATE_CHANGED, derive.STATE_PRE_REVIEWED, derive.STATE_NOT_REVIEWED}
)


@dataclass
class _Snapshot:
    """Everything the screen paints, loaded from the core on (re)load.

    `no_repo` is the named `no repo` state; `no_registry` a usable git repo with
    no `reqharness/` yet; `config_error` names a config refusal; `read_only` is
    derived — signing is possible only while the chain verifies.
    """

    root: Path | None = None
    status: str = "no repo"
    no_repo: bool = False
    no_registry: bool = False
    config_error: str = ""
    report: chain.ChainReport | None = None
    config: object | None = None
    canon: tuple[derive.CanonObject, ...] = ()
    derivation: derive.Derivation | None = None
    verdict: release.Verdict | None = None
    scan: reviews.ReviewScan | None = None
    viewer_id: str = ""
    viewer_known: bool = False
    viewer_ambiguous: bool = False
    identity_email: str = ""
    identity_name: str = ""

    @property
    def read_only(self) -> bool:
        return self.config_error != "" or not (
            self.report is not None and self.report.ok
        )


@dataclass(frozen=True)
class _Row:
    obj: derive.CanonObject
    state: str
    informative: bool
    last: str


@dataclass(frozen=True)
class _SignIntent:
    object_id: str
    digest: str
    head: tuple[int, str]
    owning_batch: str


# ---------------------------------------------------------------------------
# Elision — the middle of a long `<object>`/`<viewer>` is cut, never the tail
# (U1); cell-width aware, so a wide CJK or combining run is measured honestly.
# ---------------------------------------------------------------------------


def _coerced(value: str) -> str:
    """`darkside`'s ONE row coercion (`plain`, then every row breaker as a
    space), reached through the public `fit` at the coerced width -- so these
    truncators coerce BEFORE they cut, as `LLR-COERCE.2` requires."""
    return darkside.fit(value, darkside.shown_cells(value))


def _take_cells(text: str, cells: int) -> str:
    """The longest prefix of `text` that fits in `cells` terminal cells."""
    text = _coerced(text)
    used = 0
    for index, char in enumerate(text):
        width = cell_len(char)
        if used + width > cells:
            return text[:index]
        used += width
    return text


def _elide_middle(value: str, cells: int) -> str:
    text = _coerced(value)
    if darkside.shown_cells(text) <= cells:
        return text
    if cells <= 0:
        return ""
    if cells == 1:
        return "\u2026"
    head_cells = cells // 2
    tail_cells = cells - head_cells - 1
    head = _take_cells(text, head_cells)
    tail = _take_cells(text[::-1], tail_cells)[::-1]
    return f"{head}\u2026{tail}"


def _fit_armed(object_id: str, digest: str, head: str, width: int) -> str:
    # The head hash yields first (6 hex down to 1) so a short object id stays
    # INTACT; only when even a one-hex head cannot make the full hint fit is the
    # object's middle elided (U5).  The `enter confirms` tail is never cut.
    object_text = darkside.plain(object_id)
    prefix = (
        f"{_SIGN_ARMED_HEAD}{object_text}{_SIGN_ARMED_DIGEST}{digest[:8]}"
        f"{_SIGN_ARMED_HEADWORD}"
    )
    fixed = (
        _HINT_PREFIX_CELLS
        + darkside.shown_cells(prefix)
        + darkside.shown_cells(_SIGN_ARMED_TAIL)
    )
    for head_hex in (6, 5, 4, 3, 2, 1):
        if fixed + head_hex <= width:
            return f"{prefix}{head[:head_hex]}{_SIGN_ARMED_TAIL}"
    tail = f"{_SIGN_ARMED_DIGEST}{digest[:8]}{_SIGN_ARMED_HEADWORD}{head[:6]}{_SIGN_ARMED_TAIL}"
    budget = max(
        1,
        width
        - _HINT_PREFIX_CELLS
        - darkside.shown_cells(_SIGN_ARMED_HEAD)
        - darkside.shown_cells(tail),
    )
    return f"{_SIGN_ARMED_HEAD}{_elide_middle(object_id, budget)}{tail}"


def _fit_refusal(before: str, mid: str, after: str, width: int) -> str:
    budget = max(
        1,
        width - _HINT_PREFIX_CELLS - darkside.shown_cells(before) - darkside.shown_cells(after),
    )
    return f"{before}{_elide_middle(mid, budget)}{after}"


def _refusal_parts(template: str, value: str) -> tuple[str, str, str]:
    """Split a §6.6 refusal template at its single `{...}` placeholder into
    `(before, value, after)` so `_fit_refusal` can elide the middle (F5).
    The braces are spelled `chr(123)`/`chr(125)` so they are not new string
    literals (AT-105's frozen census counts every literal)."""
    left, right = chr(123), chr(125)
    open_at = template.index(left)
    close_at = template.index(right, open_at)
    return template[:open_at], value, template[close_at + 1:]


# ---------------------------------------------------------------------------
# Loading — the screen reads the core and paints; it writes ONLY through
# `signing.sign_review`.
# ---------------------------------------------------------------------------


def _discover(workspace: Path) -> tuple[str, identity.Identity | None]:
    try:
        top = identity.repo_root(workspace)
        if top == identity.NO_REPO:
            return identity.NO_REPO, None
        return top, identity.read(Path(top))
    except (OSError, ValueError, subprocess.SubprocessError, ValidationError):
        return identity.NO_REPO, None


def _load(top: str, who: identity.Identity | None) -> _Snapshot:
    snap = _Snapshot()
    if top == identity.NO_REPO or who is None:
        snap.no_repo = True
        snap.status = identity.NO_REPO
        return snap
    root = Path(top)
    snap.root = root
    snap.identity_email = who.email
    snap.identity_name = who.name
    if not (root / REQHARNESS_DIR).is_dir():
        snap.no_registry = True
        snap.status = NO_REGISTRY
        return snap
    report = release.safe_verify(root)
    snap.report = report
    snap.status = report.status
    try:
        config = load_config(root)
    except ValidationError as exc:
        snap.config_error = darkside.plain(str(exc))
        return snap
    snap.config = config
    try:
        canon, _ = derive.load_canon(root)
    except ValidationError:
        canon = ()
    snap.canon = canon
    scan = reviews.load_reviews(root)
    snap.scan = scan
    snap.derivation = derive.derive_states(canon, scan, report, config)
    snap.verdict = release.evaluate(config, report, snap.derivation)
    hashed = email_sha256(who.email)
    matches = [person.id for person in config.people if person.email_sha256 == hashed]
    if len(matches) == 1:
        snap.viewer_id = matches[0]
        snap.viewer_known = True
    elif len(matches) > 1:
        snap.viewer_ambiguous = True
    return snap


# ---------------------------------------------------------------------------
# Painting — Text sinks only (R10); darkside tokens only; file-derived text
# coerced through darkside.plain first.
# ---------------------------------------------------------------------------


def _cap_line(text: Text, width: int) -> Text:
    text.truncate(max(width, 1), overflow="ellipsis")
    return text


def _object_rows(snap: _Snapshot) -> list[_Row]:
    """The object table rows — derived states read, never re-derived
    (M-RS1 re-computes them here)."""
    verifiable = snap.derivation.verifiable if snap.derivation else False
    states = snap.derivation.states if snap.derivation else {}
    marks = set(snap.derivation.informative_marks) if snap.derivation else set()
    by_object: dict[str, list] = {}
    if snap.scan is not None:
        for event in snap.scan.events:
            by_object.setdefault(event.object, []).append(event)
    rows: list[_Row] = []
    for obj in snap.canon:
        state = states.get(obj.id, derive.NOT_VERIFIABLE)
        if not verifiable:
            state = derive.NOT_VERIFIABLE
        events = sorted(by_object.get(obj.id, ()), key=lambda e: (e.time, e.name))
        last = f"{events[-1].reviewer} \u00b7 h{events[-1].roles_seq}" if events else "\u2014"
        rows.append(_Row(obj=obj, state=state, informative=obj.id in marks, last=last))
    return rows


def _viewer_text(snap: _Snapshot) -> Text:
    if snap.viewer_known:
        roles = chain.effective_roles(snap.report).get(snap.viewer_id, ())
        return Text.assemble(
            (darkside.plain(snap.viewer_id), darkside.INK),
            (f" ({'+'.join(roles)})", darkside.MUT),
        )
    if snap.identity_name or snap.identity_email:
        return Text(darkside.plain(snap.identity_name or snap.identity_email), darkside.MUT)
    return Text("")


def _status_text(snap: _Snapshot, rows: list[_Row], width: int) -> Text:
    if snap.no_repo or snap.no_registry:
        word = identity.NO_REPO if snap.no_repo else NO_REGISTRY
        return _cap_line(
            Text.assemble(
                (" chain ", f"bold {darkside.GROUND} on {darkside.ALERT}"),
                (f" {darkside.plain(word)}", darkside.ALERT),
            ),
            width,
        )
    if not snap.report.ok or snap.config_error:
        chip = Text.assemble(
            (" chain ", f"bold {darkside.GROUND} on {darkside.ALERT}"),
            (f" {darkside.plain(snap.status)}", darkside.ALERT),
        )
        chip.append(
            "  registry not verifiable \u2014 every derived state is suspended", darkside.WARN
        )
        viewer = _viewer_text(snap)
        if viewer.plain:
            chip.append("  viewer ", darkside.MUT)
            chip.append_text(viewer)
        return _cap_line(chip, width)
    chip = Text.assemble(
        (" chain ", f"bold {darkside.GROUND} on {darkside.SAGE}"),
        (" \u2713 verified", darkside.SAGE),
    )
    counts = Counter(row.state for row in rows)
    noun = "objects" if len(snap.canon) != 1 else "object"
    chip.append(f"  registry {len(snap.canon)} {noun}", darkside.INK)
    for word in _STATE_ORDER:
        if counts.get(word):
            chip.append(f"  {counts[word]} {word}", _STATE_STYLE[word])
    unentitled = len(snap.derivation.unentitled) if snap.derivation else 0
    if unentitled:
        chip.append(f"  {unentitled} unentitled review", darkside.ALERT)
    viewer = _viewer_text(snap)
    if viewer.plain:
        chip.append("  viewer ", darkside.MUT)
        chip.append_text(viewer)
    return _cap_line(chip, width)


def _filter_text(snap: _Snapshot, filt: str, shown: int, width: int) -> Text:
    return _cap_line(
        Text.assemble(
            (" filter ", f"bold {darkside.GROUND} on {darkside.STEP}"),
            (f" {filt}", darkside.INK),
            (f"  ({shown} of {len(snap.canon)})", darkside.MUT),
            (f"   4 cycles: {' \u2192 '.join(_FILTERS)}", darkside.MUT),
        ),
        width,
    )


def _list_row_text(
    row: _Row, *, selected: bool, armed: bool, width: int | None = None
) -> Text:
    if armed and selected:
        name_style = f"bold {darkside.GROUND} on {darkside.ACCENT}"
        prefix = "\u25b8 "
    elif selected:
        name_style = f"bold {darkside.INK}"
        prefix = "\u25b8 "
    else:
        name_style = darkside.INK
        prefix = "  "
    parts = Text.assemble(
        (prefix + darkside.plain(row.obj.id), name_style), ("  ", "")
    )
    parts.append(darkside.plain(row.state), _STATE_STYLE.get(row.state, darkside.MUT))
    if row.informative:
        parts.append(" \u2042", darkside.ACCENT)
    parts.append(f"   {darkside.plain(row.last)}", darkside.MUT)
    if width is not None:
        # U1/U2: a long object id (or a long reviewer tail) truncates with an
        # ellipsis to the list column width, so a row never runs into the detail
        # pane and the armed row stays readable.
        parts = _cap_line(parts, width)
    return parts


def _unentitled_names(snap: _Snapshot) -> set[str]:
    return set(snap.derivation.unentitled) if snap.derivation else set()


def _review_lines(snap: _Snapshot, row: _Row) -> list[Text]:
    events = [e for e in (snap.scan.events if snap.scan else ()) if e.object == row.obj.id]
    events = sorted(events, key=lambda e: (e.time, e.name))
    if not events:
        return [Text(_EMPTY_HISTORY, style=darkside.ASH)]
    cls = next((c for c in snap.config.classes if c.id == row.obj.class_id), None)
    normative = derive.object_digests(cls, row.obj.fields)[0] if cls else ""
    unentitled = _unentitled_names(snap)
    lines: list[Text] = []
    for index, event in enumerate(events, 1):
        head = f"{event.roles_seq}:{event.roles_hash[:8]}"
        if event.normative_digest == normative:
            digest_word, digest_style = "\u2713 matches", darkside.SAGE
        else:
            digest_word, digest_style = "\u2717 stale \u2014 content changed", darkside.ALERT
        if event.kind == "model":
            who_style = darkside.ACCENT
        elif event.name in unentitled:
            who_style = darkside.ALERT
        else:
            who_style = darkside.INK
        lines.append(
            Text.assemble(
                (f"#{index} ", darkside.MUT),
                (darkside.plain(event.time), darkside.MUT),
                ("  ", ""),
                (darkside.plain(event.reviewer), who_style),
                (f" ({event.kind})", darkside.MUT),
                (f"  head {head}", darkside.ASH),
            )
        )
        lines.append(
            Text.assemble(
                (f"      digest {darkside.plain(event.normative_digest[:12])} ", darkside.MUT),
                (digest_word, digest_style),
            )
        )
    return lines


def _detail_text(snap: _Snapshot, row: _Row | None, width: int) -> Text:
    detail_w = max(38, width // 2 - 3)
    if not snap.canon or row is None:
        return Text(_EMPTY_CANON, style=darkside.ASH)
    cls = next((c for c in snap.config.classes if c.id == row.obj.class_id), None)
    role = cls.reviewer_role if cls else ""
    lines: list[Text] = [
        Text.assemble(
            (darkside.fit(darkside.plain(row.obj.id), detail_w - 6), f"bold {darkside.INK}"),
            (
                f"  \u00b7 {darkside.plain(row.obj.class_id)} \u2192 reviewer role {darkside.plain(role)}",
                darkside.MUT,
            ),
        ),
        Text.assemble(
            ("statement  ", darkside.MUT),
            (
                darkside.fit(darkside.plain(row.obj.fields.get("statement", "")), detail_w - 11),
                darkside.ASH,
            ),
        ),
    ]
    if not snap.report.ok:
        lines.append(
            Text(
                "derived states are suspended \u2014 the chain does not verify",
                style=darkside.ALERT,
            )
        )
        return Text("\n").join(lines)
    normative = derive.object_digests(cls, row.obj.fields)[0]
    head = f"{snap.report.head[0]}:{snap.report.head[1][:8]}"
    lines.append(
        Text.assemble(
            ("digest now ", darkside.MUT),
            (normative[:12], darkside.INK),
            (f"   (bound head {head})", darkside.MUT),
        )
    )
    lines.append(Text("review history", style=f"bold {darkside.MUT}"))
    lines.extend(_review_lines(snap, row))
    unentitled = _unentitled_names(snap)
    for event in sorted(
        (e for e in (snap.scan.events if snap.scan else ()) if e.object == row.obj.id),
        key=lambda e: (e.time, e.name),
    ):
        if event.name not in unentitled:
            continue
        lines.append(
            Text.assemble(
                (" unentitled ", f"bold {darkside.GROUND} on {darkside.ALERT}"),
                (
                    f" {darkside.plain(event.reviewer)} signed with no "
                    f"{darkside.plain(role)} role at head "
                    f"{event.roles_seq}:{event.roles_hash[:8]}", darkside.ALERT
                ),
            )
        )
    if row.informative:
        lines.append(
            Text.assemble(
                (" \u2042 ", f"bold {darkside.GROUND} on {darkside.ACCENT}"),
                (f" {derive.INFORMATIVE_MARK}", darkside.ACCENT),
            )
        )
    lines.append(Text(""))
    lines.append(_sign_line(snap, row))
    return Text("\n").join(lines)


def _sign_line(snap: _Snapshot, row: _Row) -> Text:
    cls = next((c for c in snap.config.classes if c.id == row.obj.class_id), None)
    role = cls.reviewer_role if cls else ""
    if not snap.viewer_known:
        return Text.assemble(
            (" b ", f"bold {darkside.GROUND} on {darkside.MUT}"),
            (" mark reviewed", darkside.MUT),
        )
    if role in chain.effective_roles(snap.report).get(snap.viewer_id, ()):
        return Text.assemble(
            (" b ", f"bold {darkside.GROUND} on {darkside.ACCENT}"),
            (
                f" mark reviewed \u2014 {darkside.plain(snap.viewer_id)} "
                f"holds {darkside.plain(role)}",
                darkside.ACCENT,
            ),
        )
    return Text.assemble(
        (" b ", f"bold {darkside.GROUND} on {darkside.WARN}"),
        (f" {darkside.plain(snap.viewer_id)} holds no {darkside.plain(role)} role", darkside.WARN),
    )


def _loading_band() -> Panel:
    """The release band while the first snapshot loads (U4): the prototype
    heading, no verdict line, no rules."""
    return Panel(
        "",
        title="release readiness",
        box=box.ROUNDED,
        border_style=darkside.STEP,
        style=f"on {darkside.PANEL}",
    )


def _band_text(snap: _Snapshot, width: int) -> Panel:
    if snap.no_repo:
        return Panel(
            Text.assemble(
                (f"{identity.NO_REPO} \u00b7 ", darkside.ALERT),
                ("not ready \u00b7 no repo", darkside.WARN),
            ),
            box=box.ROUNDED,
            border_style=darkside.STEP,
            style=f"on {darkside.PANEL}",
        )
    if snap.no_registry:
        return Panel(
            Text.assemble(
                (f"{darkside.plain(NO_REGISTRY)} \u00b7 ", darkside.ALERT),
                (darkside.plain(VERDICT_NO_REGISTRY), darkside.WARN),
            ),
            box=box.ROUNDED,
            border_style=darkside.STEP,
            style=f"on {darkside.PANEL}",
        )
    not_ok = not snap.report.ok or snap.config_error
    title = "release readiness \u2014 BLOCKED" if not_ok else "release readiness"
    lines: list[Text] = []
    if snap.verdict is not None:
        seen: set[str] = set()
        for rule_id, ok in snap.verdict.rules:
            if rule_id in seen:
                continue
            seen.add(rule_id)
            mark = "\u2713" if ok else "\u2717"
            mark_style = darkside.SAGE if ok else darkside.ALERT
            lines.append(
                Text.assemble((f"{rule_id} ", f"bold {darkside.INK}"), (mark, mark_style))
            )
        verdict_colour = darkside.SAGE if snap.verdict.ready else darkside.WARN
        lines.append(
            Text.assemble(
                ("verdict ", f"bold {darkside.INK}"),
                (darkside.plain(snap.verdict.text), f"bold {verdict_colour}"),
            )
        )
    return Panel(
        Group(*lines),
        title=title,
        box=box.ROUNDED,
        border_style=darkside.ALERT if not_ok else darkside.STEP,
        style=f"on {darkside.PANEL}",
    )


def _legend_text(width: int) -> Text:
    return _cap_line(
        Text.assemble(
            (" \u2042 ", darkside.ACCENT),
            ("informative mark   ", darkside.MUT),
            ("\u2713/\u2717", darkside.INK),
            (" digest matches / stale   ", darkside.MUT),
            ("b", darkside.ACCENT),
            (" sign \u2014 refused with the reason when you lack the role", darkside.MUT),
        ),
        width,
    )


# ---------------------------------------------------------------------------
# The object list — a line-based ScrollView that binds NO keys (A6 / D4).
# ---------------------------------------------------------------------------


class ReviewList(ScrollView):
    """A line-based `ScrollView` with a `render_line` method that binds NO keys.

    It holds the pre-rendered row `Text`s and a cursor index, scrolls so the
    cursor row stays in view, and repaints only the cursor-sized window — the
    number of `render_line` calls per cursor move is constant across N (AT-099).
    """

    # `overflow-x: hidden`: a horizontal scrollbar would take the viewport's last
    # row, so the cursor row at the bottom of the window would paint under it.
    DEFAULT_CSS = """
    ReviewList { width: 1fr; height: 100%; overflow-x: hidden; }
    """

    # The screen owns the keys (up/down/4/b/enter); the widget binds NO keys
    # and must NOT be focusable, or a focused ScrollView would swallow `down`
    # as its own scroll before the seat's `next_object` ever dispatches.
    can_focus = False

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._rows: list[Text] = []
        self.cursor = 0

    def set_rows(self, rows: list[Text], cursor: int) -> None:
        self._rows = rows
        self.cursor = min(max(0, cursor), max(0, len(rows) - 1))
        self.virtual_size = Size(self.size.width or 80, max(1, len(rows)))
        self.scroll_to_cursor()
        self.refresh()

    def set_row(self, index: int, text: Text) -> None:
        if 0 <= index < len(self._rows):
            self._rows[index] = text
            self.refresh_lines(index, 1)

    def scroll_to_cursor(self) -> None:
        height = self.size.height or 1
        top = self.scroll_offset.y
        if self.cursor < top:
            self.scroll_to(y=self.cursor, animate=False)
        elif self.cursor >= top + height:
            self.scroll_to(y=self.cursor - height + 1, animate=False)

    def render_line(self, y: int) -> Strip:
        index = y + self.scroll_offset.y
        if 0 <= index < len(self._rows):
            lines = self.app.console.render_lines(self._rows[index], pad=False)
            return Strip(lines[0]) if lines else Strip.blank(self.size.width)
        return Strip.blank(self.size.width)


# ---------------------------------------------------------------------------
# The screen
# ---------------------------------------------------------------------------


def _hint_text(text: str, style: str) -> Text:
    return Text.assemble(("next \u25b8 ", darkside.MUT), (darkside.plain(text), style))


class ReviewScreen(Screen):
    """The ReqHarness review / signing screen — variant A (B-134)."""

    KEY_SCOPE = SCOPE_REVIEW
    BINDINGS = screen_bindings(SCOPE_REVIEW)

    CSS = f"""
    #review-body {{ height: 1fr; }}
    #review-detail {{ width: 46; }}
    #review-band {{ height: {_BAND_HEIGHT}; }}
    """

    def __init__(self) -> None:
        super().__init__()
        self._snap = _Snapshot()
        self._loaded = False
        self._gen = 0
        self._sign_gen = 0
        self._sign_job = None  # the in-flight sign worker (N2)
        self._load_job = None  # the current load worker (N2)
        self._filt = "all"
        self._cursor = 0
        self._armed: _SignIntent | None = None
        self._signing = False
        self._refusal: str | None = None
        self._refusal_style: str = darkside.MUT
        self._all_rows: list[_Row] = []
        self._rows: list[_Row] = []
        self._row_texts: list[Text] = []

    def compose(self) -> ComposeResult:
        yield TabStrip(None, crumb=["home", "review"])
        yield Static(id="review-status")
        yield Static(id="review-filter")
        with Horizontal(id="review-body"):
            yield ReviewList(id="review-list")
            yield Static(id="review-detail")
        yield Static(id="review-legend")
        yield Static(id="review-band")
        yield HintLine("")
        yield KeyBar(self._bar_groups())

    # -- key bar -------------------------------------------------------------

    def _bar_groups(self) -> list[tuple[str, list[tuple[str, str]]]]:
        groups = groups_for_keybar(keybar_groups(self.KEY_SCOPE))
        if not self._loaded:
            out: list[tuple[str, list[tuple[str, str]]]] = []
            for header, rows in groups:
                kept = [row for row in rows if row[0] == "esc"]
                if kept:
                    out.append((header, kept))
            return out
        review_header = group_header("review")
        out = []
        for header, rows in groups:
            if header == review_header:
                if self._armed is not None:
                    out.append((header, [("\u21b5", _KEYBAR_ARMED)]))
                    continue
                # Not armed: `↵` (enter) is inert and is never advertised; `b`
                # marks.  Both are hidden while signing or read-only (U3).
                rows = [row for row in rows if row[0] != "\u21b5"]
                if self._signing or self._snap.read_only:
                    rows = [row for row in rows if row[0] != "b"]
            out.append((header, rows))
        return out

    # -- loading -------------------------------------------------------------

    def on_mount(self) -> None:
        self.query_one("#review-band", Static).update(_loading_band())
        self._start()

    def on_screen_resume(self) -> None:
        self._start()

    def _start(self) -> None:
        self._gen += 1
        self._load_job = self._load_worker(Path(self.app.store.workspace), self._gen)  # type: ignore[attr-defined]

    @work(thread=True, exit_on_error=False)
    def _load_worker(self, workspace: Path, gen: int):
        return gen, _load(*_discover(workspace))

    def on_worker_state_changed(self, event) -> None:
        if event.state is WorkerState.ERROR:
            # N2: only the in-flight sign worker may clear `_signing`; only the
            # CURRENT load worker may paint a failure; a stale worker is ignored.
            if event.worker is self._sign_job:
                self._handle_worker_error()
            elif event.worker is self._load_job and not self._signing:
                self._handle_worker_error()
            return
        if event.state is not WorkerState.SUCCESS:
            return
        result = event.worker.result
        if not isinstance(result, tuple) or len(result) != 2:
            return
        token, payload = result
        if isinstance(payload, tuple) and payload and payload[0] == "sign":
            if token != self._sign_gen:  # N1: only the latest sign's result
                return
            # The sign worker carries its OWN token; a sign result is never
            # dropped by the load generation, so `_signing` always clears (F1).
            self._finish_sign(payload)
            return
        if token != self._gen or not self.is_attached:
            return
        self._snap = payload
        self._loaded = True
        self._armed = None  # F3: a re-discovery cancels the arm
        self._all_rows = _object_rows(payload)
        self.query_one(KeyBar).set_groups(self._bar_groups())
        self._paint()

    # -- painting ------------------------------------------------------------

    def _filter_rows(self) -> list[_Row]:
        if self._filt == "all":
            return list(self._all_rows)
        if self._filt == _FILTER_NEEDS_ACTION:
            return [r for r in self._all_rows if r.state in _NEEDS_ACTION_STATES]
        return [r for r in self._all_rows if r.state == self._filt]

    def _armed_object(self) -> str:
        return self._armed.object_id if self._armed is not None else ""

    def _selected_row(self) -> _Row | None:
        if not self._rows:
            return None
        return self._rows[min(self._cursor, len(self._rows) - 1)]

    def _paint(self) -> None:
        """Full repaint: status, filter, list, detail, legend, band, hint."""
        snap = self._snap
        width = self.size.width
        self._rows = self._filter_rows()
        self._cursor = min(self._cursor, max(0, len(self._rows) - 1)) if self._rows else 0
        selected = self._selected_row()
        self.query_one("#review-status", Static).update(_status_text(snap, self._all_rows, width))
        self.query_one("#review-filter", Static).update(
            _filter_text(snap, self._filt, len(self._rows), width)
        )
        self._build_row_texts()
        self.query_one("#review-list", ReviewList).set_rows(self._row_texts, self._cursor)
        self.query_one("#review-detail", Static).update(_detail_text(snap, selected, width))
        self.query_one("#review-legend", Static).update(_legend_text(width))
        self.query_one("#review-band", Static).update(_band_text(snap, width))
        self.query_one(KeyBar).set_groups(self._bar_groups())
        self._paint_hint(width)

    def _list_column_width(self) -> int:
        """The list's content budget: its own width minus a one-cell gap so a
        row never runs into the detail pane (U2)."""
        return max(1, self.query_one(ReviewList).size.width - 1)

    def _build_row_texts(self) -> None:
        armed = self._armed is not None
        armed_obj = self._armed_object()
        width = self._list_column_width()
        self._row_texts = [
            _list_row_text(
                r,
                selected=(i == self._cursor),
                armed=(armed and r.obj.id == armed_obj),
                width=width,
            )
            for i, r in enumerate(self._rows)
        ]

    def _row_text(self, index: int) -> Text:
        r = self._rows[index]
        armed = self._armed is not None
        return _list_row_text(
            r,
            selected=(index == self._cursor),
            armed=(armed and r.obj.id == self._armed_object()),
            width=self._list_column_width(),
        )

    def _paint_hint(self, width: int) -> None:
        if self._armed is not None:
            hint = _fit_armed(
                self._armed.object_id, self._armed.digest, self._armed.head[1], width
            )
            self.query_one(HintLine).update(_hint_text(hint, darkside.ACCENT))
        elif self._refusal is not None:
            self.query_one(HintLine).update(_hint_text(self._refusal, self._refusal_style))
        else:
            self.query_one(HintLine).update(_hint_text(self._hint(), darkside.MUT))

    def _paint_detail(self, width: int) -> None:
        self.query_one("#review-detail", Static).update(
            _detail_text(self._snap, self._selected_row(), width)
        )

    def _hint(self) -> str:
        snap = self._snap
        if not self._loaded:
            return ""
        # Only §6.6 / approved-prototype copy may rest on the hint line: with no
        # repo or an undeclared viewer the status chip and band already say so,
        # and `b` answers with its REFUSE-* line.
        if snap.no_repo:
            return ""
        if snap.no_registry or snap.read_only:
            return _READ_ONLY_HINT
        if snap.viewer_ambiguous:
            return _REFUSE_AMBIGUOUS
        if not snap.viewer_known:
            return ""
        roles = "+".join(chain.effective_roles(snap.report).get(snap.viewer_id, ()))
        return _REST_HINT.format(viewer=snap.viewer_id, roles=roles)

    # -- arm / sign ----------------------------------------------------------

    def _arm_reason(self) -> str | None:
        """The arm-time entitlement check over the snapshot (no disk)."""
        snap = self._snap
        if snap.no_repo or snap.no_registry or snap.config_error:
            return signing.REASON_NO_REGISTRY
        if not snap.report.ok:
            return signing.chain_reason(snap.report)
        if snap.viewer_ambiguous:
            return signing.REASON_AMBIGUOUS_VIEWER
        if not snap.viewer_known:
            return signing.REASON_UNKNOWN_VIEWER
        row = self._selected_row()
        if row is None:
            return signing.REASON_UNKNOWN_OBJECT
        ok, reason = signing.entitlement(
            snap.report, snap.config, snap.canon, snap.viewer_id, row.obj.id
        )
        return None if ok else reason

    def _paint_chain_refusal(self, status: str) -> None:
        """The §6.6 REFUSE-CHAIN line with a given status (F5)."""
        width = self.size.width
        self._set_refusal(
            _fit_refusal(*_refusal_parts(_REFUSE_CHAIN, status), width), darkside.ALERT
        )

    def _paint_templated(self, template: str, value: str) -> None:
        """Paint a single-placeholder §6.6 refusal with the ALERT token (F5)."""
        self._set_refusal(
            _fit_refusal(*_refusal_parts(template, value), self.size.width), darkside.ALERT
        )

    def _handle_worker_error(self) -> None:
        """A worker failed with a non-refusal exception (F2): `exit_on_error=False`
        keeps the app up, the in-flight sign clears, and the hint paints the
        §6.6 REFUSE-CHAIN line with the core's `chain broken` status — the one
        status word the requirements give an unexpected failure."""
        self._signing = False
        self._armed = None
        self._refusal = None
        self._paint_chain_refusal(chain.STATUS_BROKEN)
        self.query_one(KeyBar).set_groups(self._bar_groups())

    def _paint_refusal(self, reason: str) -> None:
        snap = self._snap
        viewer = darkside.plain(snap.identity_name or snap.identity_email)
        row = self._selected_row()
        obj_id = darkside.plain(row.obj.id) if row is not None else ""
        cls = next((c for c in snap.config.classes if c.id == row.obj.class_id), None) if row else None
        role = cls.reviewer_role if cls else ""
        if reason in (
            signing.REASON_TAMPERED,
            signing.REASON_FORKED,
            signing.REASON_NO_REGISTRY,
            signing.REASON_UNAPPROVED_CONFIG,
        ):
            status = snap.status if not snap.no_registry else NO_REGISTRY
            self._paint_chain_refusal(status)
        elif reason == signing.REASON_AMBIGUOUS_VIEWER:
            self._set_refusal(_REFUSE_AMBIGUOUS, darkside.ALERT)
        elif reason == signing.REASON_UNKNOWN_VIEWER:
            self._paint_templated(_REFUSE_VIEWER, viewer)
        elif reason == signing.REASON_UNKNOWN_OBJECT:
            self._paint_templated(_REFUSE_OBJECT, obj_id)
        elif reason == signing.REASON_RETIRED:
            self._paint_templated(_REFUSE_RETIRED, obj_id)
        elif reason == signing.REASON_CLASS_UNDECLARED:
            self._paint_templated(_REFUSE_CLASS, obj_id)
        elif reason == REASON_NO_ROLE:
            template = _REFUSE_NO_ROLE.replace("{role}", role)
            self._paint_templated(template, viewer)
        elif reason == REASON_AUTHOR:
            self._paint_templated(_REFUSE_AUTHOR, viewer)
        elif reason in (
            signing.REASON_MOVED_OBJECT,
            signing.REASON_MOVED_DIGEST,
            signing.REASON_MOVED_HEAD,
            signing.REASON_MOVED_ROLE,
        ):
            self._set_refusal(_REFUSE_MOVED, darkside.WARN)
        elif reason == signing.REASON_ALREADY_SIGNED:
            self._set_refusal(_REFUSE_DUP, darkside.ALERT)
        elif reason == signing.REASON_REVIEW_LIMIT:
            self._set_refusal(_REFUSE_LIMIT, darkside.ALERT)
        else:
            self._set_refusal(darkside.plain(reason), darkside.ALERT)

    def _set_refusal(self, text: str, style: str) -> None:
        self._refusal = text
        self._refusal_style = style
        self.query_one(HintLine).update(_hint_text(text, style))

    def action_sign(self) -> None:
        if not self._loaded:
            return
        if self._signing:
            return
        if self._armed is not None:
            self._cancel_arm()
            return
        reason = self._arm_reason()
        if reason is not None:
            if reason == signing.REASON_UNKNOWN_OBJECT:
                return  # an empty canon: `b` is inert, no refusal with a missing name
            self._paint_refusal(reason)
            return
        row = self._selected_row()
        cls = next((c for c in self._snap.config.classes if c.id == row.obj.class_id), None)
        normative = derive.object_digests(cls, row.obj.fields)[0]
        self._armed = _SignIntent(
            object_id=row.obj.id,
            digest=normative,
            head=self._snap.report.head,
            owning_batch=row.obj.owning_batch,
        )
        self._refusal = None
        self.query_one(ReviewList).set_row(self._cursor, self._row_text(self._cursor))
        self.query_one(KeyBar).set_groups(self._bar_groups())
        self._paint_hint(self.size.width)

    def action_confirm(self) -> None:
        if self._armed is None or self._signing:
            return
        intent = self._armed
        self._armed = None
        self._signing = True
        self._refusal = None
        self.query_one(ReviewList).set_row(self._cursor, self._row_text(self._cursor))
        self.query_one(KeyBar).set_groups(self._bar_groups())
        self._paint_hint(self.size.width)
        self._sign_gen += 1
        self._sign_job = self._sign_worker(intent, self._snap.root, self._sign_gen)

    @work(thread=True, exit_on_error=False)
    def _sign_worker(self, intent: _SignIntent, root: Path | None, sign_token: int):
        if root is None:
            return sign_token, ("sign", "refused", signing.REASON_NO_REGISTRY, None)
        try:
            who = identity.read(root)
        except (OSError, ValueError, subprocess.SubprocessError):
            who = identity.Identity("", "")
        try:
            path = signing.sign_review(
                root,
                intent.object_id,
                who.email,
                confirm_digest=intent.digest,
                confirm_head=intent.head,
                confirm_owning_batch=intent.owning_batch,
            )
        except SigningRefused as exc:
            return sign_token, ("sign", "refused", exc.reason, None)
        except OSError:
            # F2: a write failure (e.g. PermissionError) is an unexpected
            # failure, refused with the core's `chain broken` status.
            return sign_token, ("sign", "refused", signing.REASON_NO_REGISTRY, chain.STATUS_BROKEN)
        return sign_token, ("sign", "signed", str(path))

    def _finish_sign(self, payload: tuple) -> None:
        self._signing = False
        self._armed = None
        status = payload[1]
        if status == "signed":
            self._refusal = None
            self._start()
            return
        reason = payload[2]
        override = payload[3] if len(payload) > 3 else None
        if override is not None:
            self._paint_chain_refusal(override)
        else:
            self._paint_refusal(reason)
        self.query_one(KeyBar).set_groups(self._bar_groups())

    # -- navigation / filter -------------------------------------------------

    def _cancel_arm(self) -> None:
        if self._armed is None and self._refusal is None:
            return
        self._armed = None
        self._refusal = None
        self.query_one(ReviewList).set_row(self._cursor, self._row_text(self._cursor))
        self.query_one(KeyBar).set_groups(self._bar_groups())
        self._paint_hint(self.size.width)

    def on_key(self, event) -> None:
        # The copy promises "any other key cancels", bound or not (`down`, `4`,
        # `x`, `space`): this one hook disarms before the key's own action runs,
        # or a later `enter` would still sign.  `enter` confirms; `b` toggles in `action_sign`; `escape`/`q` cancel in
        # `action_home` (which must still see the arm, or it would leave).
        if self._armed is not None and event.key not in ("enter", "b", "escape", "q"):
            self._cancel_arm()

    def action_next_object(self) -> None:
        self._move(1)

    def action_prev_object(self) -> None:
        self._move(-1)

    def _move(self, delta: int) -> None:
        if not self._loaded:
            return
        if not self._rows:
            return
        old = self._cursor
        self._cursor = (self._cursor + delta) % len(self._rows)
        listing = self.query_one(ReviewList)
        listing.set_row(old, self._row_text(old))
        listing.set_row(self._cursor, self._row_text(self._cursor))
        listing.cursor = self._cursor
        listing.scroll_to_cursor()
        width = self.size.width
        self._paint_detail(width)
        self._paint_hint(width)

    def action_filter(self) -> None:
        if not self._loaded:
            return
        index = _FILTERS.index(self._filt)
        self._filt = _FILTERS[(index + 1) % len(_FILTERS)]
        self._cursor = 0
        self._paint()

    def action_home(self) -> None:
        if self._armed is not None:
            self._cancel_arm()
            return
        self.app.pop_screen()
