"""HLR-RH.8 — the roles screen (matrix variant B): AT-077a/b/c, AT-078,
AT-079, AT-082, AT-083 of batch `2026-10-11-reqharness-batch` (increments
RH6a + RH6b).

The node names are the executed verification named in
`.dev-flow/2026-10-11-reqharness-batch/01-requirements.md` §3 for HLR-RH.8.
AT-082 (admin `a`/`r` pending resolution, LLR-RH.8.6) is increment RH6b;
fork recovery is core-only (B-126) — AT-083 asserts detection +
exclusion ON SCREEN only.

Every drive is `MapperApp(tmp_path)` + `run_test(size=(W, 34))` + real
`pilot.press` keys; key presses route through the `tests/test_draft_save.py`
helpers instead of new ones.  The seeded repo IS the app workspace, so repo
discovery (D13) finds it through `git rev-parse --show-toplevel`.
"""
from __future__ import annotations

import ast
import asyncio
import hashlib
import os
import re
import subprocess
import unicodedata
from pathlib import Path

import pytest
import yaml
from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text
from textual.widgets import Static

from mapper import darkside
from mapper.app import HomeScreen, MapperApp
import mapper.reqharness.chain as chain_module
from mapper.reqharness.canonical import chain_hash
from mapper.reqharness.chain import append_policy, propose, verify_chain
from mapper.reqharness.config import (
    create_registry,
    email_sha256,
    load_config,
    load_documents,
)
from mapper.reqharness.pending import list_pending
from mapper.screens.roles import (
    GLYPH_IN_FORCE,
    GLYPH_NOT_HELD,
    GLYPH_PENDING_ADD,
    GLYPH_PENDING_REMOVE,
    RolesScreen,
    _Snapshot,
    _matrix_renderable,
)
from mapper.widgets.chrome import HintLine, KeyBar
from tests.test_draft_save import _press

T0 = "2026-10-11T09:00:00Z"
T1 = "2026-10-11T09:01:00Z"
T2 = "2026-10-11T09:02:00Z"
T3 = "2026-10-11T09:03:00Z"

ROLES = ("admin", "req-reviewer", "safety-lead", "board", "qa")
ROLES_FILE = Path("reqharness") / "roles.yml"
CONFIG_FILE = Path("reqharness") / "config.yml"
WIDTHS = [118, 87]

SUBJECT = ("subject", "username_subject", "username_subject@example.invalid")
REVIEWER2 = ("reviewer-2", "Reviewer Two", "r2@example.invalid")


# ---------------------------------------------------------------------------
# Fixtures — a seeded registry whose repo root IS the app workspace
# ---------------------------------------------------------------------------


def _fixture_env(tmp_path: Path) -> dict[str, str]:
    """The env of the FIXTURE-CREATION subprocesses only: `GIT_CONFIG_GLOBAL`
    at a temp file, so `git init` / `git config` never touch the operator's
    real git config (the same fixture-env pattern as
    `tests/test_reqharness_identity.py`)."""
    return {**os.environ, "GIT_CONFIG_GLOBAL": str(tmp_path / "global.gitconfig")}


def _git(repo: Path, *args: str, env: dict[str, str]) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, f"git {' '.join(args)}: {result.stderr}"
    return result.stdout


def _init_repo(tmp_path: Path) -> dict[str, str]:
    env = _fixture_env(tmp_path)
    init = subprocess.run(
        ["git", "init", "-q", str(tmp_path)], env=env,
        capture_output=True, text=True, encoding="utf-8",
    )
    assert init.returncode == 0, init.stderr
    return env


def _set_identity(root: Path, env: dict[str, str], person: tuple[str, str, str]) -> None:
    """Repo-local git identity — the injection point the viewer is read from."""
    _git(root, "config", "user.name", person[1], env=env)
    _git(root, "config", "user.email", person[2], env=env)


def _add_person(root: Path, person: tuple[str, str, str], now: str) -> None:
    """Add a person to the config, then re-bind it through an admin `policy`
    event (the edited config is otherwise `config changed without
    approval`) — the same shape as `tests/test_reqharness_chain.py`."""
    path = root / CONFIG_FILE
    (document,) = load_documents(
        path.read_text(encoding="utf-8"), where="reqharness/config.yml"
    )
    document["people"].append(
        {
            "id": person[0],
            "name": person[1],
            "email_sha256": email_sha256(person[2]),
        }
    )
    path.write_text(
        yaml.safe_dump(document, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
        newline="\n",
    )
    append_policy(root, approved_by="subject", note=f"add {person[0]}", now=now)


def _seed_team(tmp_path: Path, env: dict[str, str]) -> None:
    """subject (genesis admin) + reviewer-2, who holds req-reviewer through
    one admin grant: 3 verified events."""
    create_registry(
        tmp_path, person=SUBJECT[0], name=SUBJECT[1], email=SUBJECT[2],
        roles=ROLES, now=T0,
    )
    _add_person(tmp_path, REVIEWER2, T1)
    from mapper.reqharness.chain import propose

    assert propose(
        tmp_path, requester="subject", action="grant",
        person="reviewer-2", role="req-reviewer", now=T2,
    ) is None  # an admin on someone else: one event, applied


def _roles_sha(root: Path) -> str:
    return hashlib.sha256((root / ROLES_FILE).read_bytes()).hexdigest()


def _pending_files(root: Path) -> list[Path]:
    directory = root / "reqharness" / "pending"
    return sorted(directory.glob("*.yml")) if directory.is_dir() else []


def _read_docs(root: Path) -> list[dict]:
    return load_documents(
        (root / ROLES_FILE).read_text(encoding="utf-8"), where="reqharness/roles.yml"
    )


def _write_docs(root: Path, docs: list[dict]) -> None:
    text = "".join(
        "---\n" + yaml.safe_dump(d, sort_keys=False, allow_unicode=True) for d in docs
    )
    (root / ROLES_FILE).write_text(text, encoding="utf-8", newline="\n")


def _fork_event(prev: str, seq: int, *, time: str, person: str, role: str,
                note: str) -> dict:
    """One fork child claiming *prev* — a full event document with a valid
    link, the same shape as `tests/test_reqharness_chain.py::_fork_parts`."""
    body = {
        "seq": seq,
        "time": time,
        "requested_by": "subject",
        "approved_by": "subject",
        "action": "grant",
        "person": person,
        "role": role,
        "note": note,
        "roles_seq": seq - 1,
        "roles_hash": prev,
        "prev_hash": prev,
    }
    body["this_hash"] = chain_hash(prev, body)
    return body


# ---------------------------------------------------------------------------
# Screen reading helpers
# ---------------------------------------------------------------------------


def _plain(screen, widget_id: str) -> str:
    content = screen.query_one(f"#{widget_id}").content
    return getattr(content, "plain", str(content))


def _render_text(screen, widget_id: str, width: int) -> str:
    """Paint a widget's rich content (Table/Group/Panel) to plain text at
    `width` columns — the width the widget occupies — so the line lengths
    and wrap behaviour asserted are the painted ones."""
    content = screen.query_one(f"#{widget_id}", Static).content
    # width AND height: with only width set, a `TERM=dumb` environment (the
    # test harness sets one) short-circuits rich's size to the 80x25 default
    # color_system=None: every caller asserts on the TEXT of this capture, so
    # the render must be plain no matter what the ambient shell exports
    # (FORCE_COLOR, a tty, ...) — never ANSI-styled (`release [..m ready`).
    console = Console(width=width, height=34, legacy_windows=False,
                      color_system=None)
    with console.capture() as capture:
        console.print(content)
    return capture.get().rstrip("\n")


def _row(body: str, person_id: str) -> str:
    for line in body.splitlines():
        if person_id in line and ("\u25cf" in line or "\u25cb" in line
                                  or "\u25d0" in line or "\u25cc" in line):
            return line
    raise AssertionError(f"no matrix row for {person_id!r} in:\n{body}")


async def _open_roles(app: MapperApp, pilot) -> RolesScreen:
    await _press(pilot, "R")
    screen = app.screen
    assert isinstance(screen, RolesScreen), type(screen)
    # B-127: the git discovery runs on a worker; the first paint lands when it
    # returns, so every drive waits for it before reading the frame.
    # Bounded (fix-batch increment 003 review L2): a worker that stops
    # self-bounding fails here by name instead of hanging the suite.
    await asyncio.wait_for(app.workers.wait_for_complete(), timeout=60)
    await pilot.pause()
    return screen


async def _goto(pilot, row: int, col: int) -> None:
    """Drive the cursor from (0,0) to (row, col) with real movement keys."""
    for _ in range(row):
        await _press(pilot, "j")
    for _ in range(col):
        await _press(pilot, "l")


# ---------------------------------------------------------------------------
# AT-077a — home door opens the screen; the matrix paints at 118 AND 87
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("width", WIDTHS)
async def test_at_077a_roles_screen_opens_from_home_and_paints_matrix(
        tmp_path, width):
    """LLR-RH.8.1: home -> `R` opens the roles screen; the matrix paints
    people x roles with the four glyphs; the genesis event paints verbatim;
    the key bar advertises the seat's `space` row."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, SUBJECT)
    _seed_team(tmp_path, env)
    # all four glyphs on one matrix: ana holds board (●), reviewer-2's own
    # grant pends (◐ on reviewer-2), ana's own revoke pends (◌ on ana) —
    # self-changes and non-admin proposals stay pending by rule.
    _add_person(tmp_path, ("ana", "Ana", "ana@example.invalid"), T3)
    propose(tmp_path, requester="subject", action="grant",
            person="ana", role="board", now=T3)
    propose(tmp_path, requester="reviewer-2", action="grant",
            person="reviewer-2", role="safety-lead", now=T3)
    propose(tmp_path, requester="ana", action="revoke",
            person="ana", role="board", now=T3)

    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        await pilot.pause()
        assert isinstance(app.screen, HomeScreen)
        home_text = app.screen._empty_text().plain  # noqa: SLF001
        assert "R roles" in home_text, home_text
        screen = await _open_roles(app, pilot)
        status = _plain(screen, "roles-status")
        body = _render_text(screen, "roles-body", width)
        band = _render_text(screen, "roles-band", width)
        bar = screen.query_one(KeyBar).content
        bar_text = getattr(bar, "plain", str(bar))

    assert "\u2713 verified" in status, status
    assert "viewer subject" in status, status
    # every seeded person x role cell is present with the expected glyph
    subject_row = _row(body, "subject")
    reviewer_row = _row(body, "reviewer-2")
    ana_row = _row(body, "ana")
    assert GLYPH_IN_FORCE in subject_row and GLYPH_NOT_HELD in subject_row, subject_row
    assert GLYPH_IN_FORCE in reviewer_row and GLYPH_PENDING_ADD in reviewer_row, reviewer_row
    assert GLYPH_PENDING_REMOVE in ana_row and GLYPH_NOT_HELD in ana_row, ana_row
    # the genesis event paints verbatim (LLR-RH.8.1)
    assert "genesis \u2014 declared at registry creation" in body, body
    # the band carries the status, the count, the head hash and the verdict
    assert "\u2713 verified" in band, band
    assert "5 events" in band, band
    assert "head " in band, band
    assert "pending (2)" in band, band
    assert "release ready" in band, band
    # the key bar reads the seat (glyph + label); at 87 columns the `space`
    # row folds into the bar's `+N` overflow — the roles group still leads
    if width == 118:
        assert "space" in bar_text and "propose change" in bar_text, bar_text
    else:
        assert "j next person" in bar_text, bar_text


# ---------------------------------------------------------------------------
# AT-077b — the footer band detail, in verified AND pending-bearing states
# ---------------------------------------------------------------------------


async def test_at_077b_status_band_shows_chain_head_viewer_and_pending(tmp_path):
    """LLR-RH.8.3: all six band elements — event count, head hash, viewer
    identity (pinned by the injected repo-local git config), pending detail
    (count + newest request), chain status, release verdict — in the
    verified state and with a pending request on disk."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, REVIEWER2)  # the viewer is a non-admin
    _seed_team(tmp_path, env)
    from mapper.reqharness.chain import propose

    # a pending self-change: written as a request file, roles.yml untouched
    assert propose(tmp_path, requester="reviewer-2", action="grant",
                   person="reviewer-2", role="safety-lead", now=T3) is not None
    head = verify_chain(tmp_path).events[-1].this_hash

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        status = _plain(screen, "roles-status")
        band = _render_text(screen, "roles-band", 118)

    assert "\u2713 verified" in status, status
    assert "viewer reviewer-2" in status, status
    # 1 event count · 2 head hash (12 hex + the ellipsis) · 3 viewer (status
    # line) · 4 pending detail
    assert "3 events" in band, band
    assert f"head {head[:12]}\u2026" in band, band
    assert f"head {head}" not in band, band
    assert "pending (1)" in band, band
    assert "reviewer-2 +safety-lead by reviewer-2" in band, band
    # 5 chain status · 6 release verdict
    assert "\u2713 verified" in band
    assert "release ready" in band, band


# ---------------------------------------------------------------------------
# AT-077c — file-derived text paints through Text sinks only (R10)
# ---------------------------------------------------------------------------


async def test_at_077c_file_derived_text_paints_through_text_sinks(tmp_path,
                                                                   monkeypatch):
    """LLR-RH.8.4/8.5: a `[bold]` payload in a person id paints literally; a
    monkeypatched darkside token changes the painted style (the token
    oracle); the source censuses find no hex colour, no glyph outside the
    sanctioned set, no non-ASCII letter, and no raw-string paint sink."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, SUBJECT)
    _seed_team(tmp_path, env)
    _add_person(tmp_path, ("eve[bold]x", "Eve", "eve@example.invalid"), T3)

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        body = _render_text(screen, "roles-body", 118)

    # the markup payload paints literally — `[bold]` survived as text
    assert "eve[bold]x" in body, body
    # the matrix renders as the prototype's Rich table (SIMPLE_HEAD rule)
    assert "\u2500" in body, body

    # the token oracle: a patched darkside token changes the painted style.
    # The matrix is a Rich `Table` + legend `Text` inside a `Group`; the
    # legend's spans carry the SAGE token, so patching SAGE must repaint.
    snap = _Snapshot(
        root=tmp_path, status="chain verified",
        people=load_config(tmp_path).people, roles=ROLES,
        held={"subject": frozenset({"admin"})},
    )
    renderable = _matrix_renderable(snap, 0, 0, 118)
    table = next(r for r in renderable._renderables if isinstance(r, Table))  # noqa: SLF001
    assert table.box is box.SIMPLE_HEAD
    legend = next(r for r in renderable._renderables if isinstance(r, Text))  # noqa: SLF001
    styles_before = {str(span.style) for span in legend.spans}
    with monkeypatch.context() as patch:
        patch.setattr(darkside, "SAGE", "#123456")
        patched = _matrix_renderable(snap, 0, 0, 118)
        legend_after = next(r for r in patched._renderables if isinstance(r, Text))  # noqa: SLF001
    styles_after = {str(span.style) for span in legend_after.spans}
    assert styles_before != styles_after, (styles_before, styles_after)
    assert any("#123456" in style for style in styles_after), styles_after


def test_at_077c_source_censuses_no_hex_no_stray_glyph_no_str_sink():
    """LLR-RH.8.5(a)(b)(c): the painting-sink, token/glyph and English-only
    censuses over `mapper/screens/roles.py`."""
    source = (Path(__file__).resolve().parent.parent
              / "mapper" / "screens" / "roles.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    hexes = re.findall(r"#[0-9a-fA-F]{6}", source)
    assert hexes == [], f"hex colour literals in the screen: {hexes}"

    sanctioned = frozenset(
        "\u25cf\u25d0\u25cc\u25cb\u25b8\u2713\u2717\u2014\u00b7\u2026"
    )
    stray = sorted({
        char for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        for char in node.value
        if ord(char) > 127 and char not in sanctioned
    })
    assert stray == [], f"glyphs outside the sanctioned set: {stray!r}"
    letters = sorted({
        char for char in "\u25cf\u25d0\u25cc\u25cb\u25b8\u2713\u2717"
        if unicodedata.category(char).startswith("L")
    })
    assert letters == [], letters

    # the sink census: no raw string reaches a paint sink.  Every `update` /
    # `notify` / `Static(...)` call's positional renderable is a function
    # call or a Text — never a string constant.
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = getattr(func, "attr", getattr(func, "id", ""))
        if name not in ("update", "notify", "Static"):
            continue
        for arg in node.args:
            assert not isinstance(arg, ast.Constant) or not isinstance(arg.value, str), (
                f"a raw string reaches the {name} sink (line {node.lineno})"
            )
    assert "markup=True" not in source

    # QA C3 (DDR follow-up): positive presence - the module DEFINES
    # the glyph constants the census and the tests rely on, and it
    # actually paints through Text sinks; an empty (or gutted) file
    # fails here instead of passing the censuses vacuously
    assigned = {
        target.id
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    for constant in (
        "GLYPH_IN_FORCE", "GLYPH_PENDING_ADD",
        "GLYPH_PENDING_REMOVE", "GLYPH_NOT_HELD",
    ):
        assert constant in assigned, f"roles.py no longer defines {constant}"
    text_sinks = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "Text"
    ]
    assert text_sinks, "roles.py defines no Text sink: the census is vacuous"



# ---------------------------------------------------------------------------
# AT-078 — propose semantics: non-admin pends, admin applies, own-change pends
# ---------------------------------------------------------------------------


async def test_at_078_non_admin_toggle_pends_admin_applies_in_one_key(tmp_path):
    """LLR-RH.8.2: as a non-admin, `space` writes a pending request (◐ add /
    ◌ remove) and roles.yml is byte-identical; as an admin, `space` on
    SOMEONE ELSE lands one event (`requested_by == approved_by`); on the
    admin's OWN cell it stays ◐ pending."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, REVIEWER2)
    _seed_team(tmp_path, env)

    # -- arm 1: the non-admin's proposals pend, both directions --------------
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        before = _roles_sha(tmp_path)
        # cursor (0,0) -> subject x safety-lead (col 2): grant -> pending add
        await _goto(pilot, 0, 2)
        await _press(pilot, "space")
        after_add = _roles_sha(tmp_path)
        body = _render_text(screen, "roles-body", 118)
        assert GLYPH_PENDING_ADD in _row(body, "subject"), _row(body, "subject")
        # -> reviewer-2 x req-reviewer (row 1, col 1): held -> pending remove
        await _press(pilot, "j")
        await _press(pilot, "h")
        await _press(pilot, "space")
        after_remove = _roles_sha(tmp_path)
        body = _render_text(screen, "roles-body", 118)
        assert GLYPH_PENDING_REMOVE in _row(body, "reviewer-2"), _row(body, "reviewer-2")
        band = _render_text(screen, "roles-band", 118)
        hint = screen.query_one(HintLine).text
    assert before == after_add == after_remove, "roles.yml moved on a pending path"
    assert len(_pending_files(tmp_path)) == 2, _pending_files(tmp_path)
    assert "pending (2)" in band, band
    assert "pending request" in hint, hint

    # -- arm 2: an admin's change about someone else is ONE event ------------
    _set_identity(tmp_path, env, SUBJECT)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        events_before = len(_read_docs(tmp_path))
        await _goto(pilot, 1, 2)  # reviewer-2 x safety-lead
        await _press(pilot, "space")
        events_after = len(_read_docs(tmp_path))
        body = _render_text(screen, "roles-body", 118)
        hint = screen.query_one(HintLine).text
    assert events_after == events_before + 1, (events_before, events_after)
    landed = _read_docs(tmp_path)[-1]
    assert landed["action"] == "grant"
    assert landed["requested_by"] == landed["approved_by"] == "subject"
    assert landed["person"] == "reviewer-2" and landed["role"] == "safety-lead"
    assert GLYPH_IN_FORCE in _row(body, "reviewer-2"), _row(body, "reviewer-2")
    assert "applied" in hint, hint

    # -- arm 3: the admin's own change stays pending --------------------------
    _set_identity(tmp_path, env, SUBJECT)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        events_before = len(_read_docs(tmp_path))
        pending_before = len(_pending_files(tmp_path))
        await _goto(pilot, 0, 3)  # subject x board: the admin's own cell
        await _press(pilot, "space")
        body = _render_text(screen, "roles-body", 118)
    assert len(_read_docs(tmp_path)) == events_before, "a self-change wrote the chain"
    assert len(_pending_files(tmp_path)) == pending_before + 1
    assert GLYPH_PENDING_ADD in _row(body, "subject"), _row(body, "subject")


# ---------------------------------------------------------------------------
# AT-079 — tampered chain: broken state painted, last verified roles, read-only
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("width", [118, 87],
                         ids=["w118", "w87-optional-per-R26"])
async def test_at_079_tampered_chain_paints_broken_state_and_blocks_release(
        tmp_path, width):
    """LLR-RH.8.2/8.3: a hand-edited roles.yml paints `config changed without
    approval` and `not ready · registry not verifiable`; the matrix shows the
    LAST VERIFIED roles; `space` is inert and paints the read-only message.
    The 87-column band arm is OPTIONAL per R26 — shipped, not silently dropped."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, SUBJECT)
    _seed_team(tmp_path, env)
    # the hand edit: reviewer-2's grant becomes an admin grant, hashes stale
    docs = _read_docs(tmp_path)
    docs[2]["role"] = "admin"
    _write_docs(tmp_path, docs)
    report = verify_chain(tmp_path)
    assert report.status == "config changed without approval"

    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        status = _plain(screen, "roles-status")
        body = _render_text(screen, "roles-body", width)
        band = _render_text(screen, "roles-band", width)
        before = _roles_sha(tmp_path)
        await _goto(pilot, 1, 2)
        await _press(pilot, "space")  # must be inert
        after = _roles_sha(tmp_path)
        hint_after = screen.query_one(HintLine).text

    assert "config changed without approval" in status, status
    assert "config changed without approval" in band, band
    assert "not ready \u00b7 registry not verifiable" in band, band
    # last verified prefix = genesis + policy: subject holds admin only
    assert GLYPH_IN_FORCE in _row(body, "subject"), _row(body, "subject")
    reviewer_row = _row(body, "reviewer-2")
    assert GLYPH_IN_FORCE not in reviewer_row, reviewer_row
    assert "2 events" in band, band
    # read-only: space wrote nothing and the message says why
    assert before == after, "space wrote to a tampered chain"
    assert "read-only" in hint_after, hint_after


# ---------------------------------------------------------------------------
# AT-083 — forked chain: exclusion shown read-only on screen (recovery is
# core-only per R16/R25 — no recovery UI here)
# ---------------------------------------------------------------------------


def _seed_fork(tmp_path: Path, env: dict[str, str]) -> None:
    """genesis + policy, then TWO children claiming the policy head — the
    parallel-merge fork.  Ana is in the config; both children grant her a
    role, so exclusion (not the grant) is what the matrix must show."""
    create_registry(
        tmp_path, person=SUBJECT[0], name=SUBJECT[1], email=SUBJECT[2],
        roles=ROLES, now=T0,
    )
    _add_person(tmp_path, ("ana", "Ana", "ana@example.invalid"), T1)
    docs = _read_docs(tmp_path)
    head = verify_chain(tmp_path).events[-1].this_hash
    child_a = _fork_event(head, 3, time=T2, person="ana", role="req-reviewer",
                          note="branch A")
    child_b = _fork_event(head, 3, time=T2, person="ana", role="board",
                          note="branch B")
    _write_docs(tmp_path, [*docs, child_a, child_b])


async def _fork_screen(tmp_path, env) -> tuple[str, str, str]:
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        return (_plain(screen, "roles-status"),
                _render_text(screen, "roles-body", 118),
                _render_text(screen, "roles-band", 118))


async def test_at_083_forked_chain_paints_excluded_and_recovers(tmp_path):
    """LLR-RH.3/8: on a forked chain both children are excluded from
    authority (deterministic on a second load), the band paints
    `chain forked at seq N`, the matrix is read-only and shows the pre-fork
    roles.  Recovery is exercised core-side (`test_fork_resolve_event_recovers`);
    this test asserts detection + exclusion ON SCREEN only."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, SUBJECT)
    _seed_fork(tmp_path, env)
    assert verify_chain(tmp_path).status == "chain forked at seq 3"

    status, body, band = await _fork_screen(tmp_path, env)
    assert "chain forked at seq 3" in status, status
    assert "chain forked at seq 3" in band, band
    assert "not ready \u00b7 registry not verifiable" in band, band
    # both children excluded: ana holds nothing, the pre-fork roles stand
    ana_row = _row(body, "ana")
    assert GLYPH_IN_FORCE not in ana_row, ana_row
    assert GLYPH_IN_FORCE in _row(body, "subject"), _row(body, "subject")
    assert "2 events" in band, band

    # read-only on screen: space writes nothing
    before = _roles_sha(tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        await _press(pilot, "space")
        hint = screen.query_one(HintLine).text
    assert _roles_sha(tmp_path) == before, "space wrote to a forked chain"
    assert "read-only" in hint, hint

    # second load: the exclusion is deterministic, byte for byte
    status2, body2, band2 = await _fork_screen(tmp_path, env)
    assert status2 == status
    assert band2 == band
    assert _row(body2, "ana") == ana_row


# ---------------------------------------------------------------------------
# RH6AF — code-review follow-up nodes (prototype-drift, width, ledger, OSError)
# ---------------------------------------------------------------------------

ROLES_SIX = ("admin", "req-reviewer", "safety-lead", "board", "qa", "auditor")
LONG_ID = "abcdefghijklmnopqrst"  # 20 chars — over the 12-cell id cap


async def test_rh6af_matrix_holds_at_87_with_six_roles_and_a_long_id(tmp_path):
    """RH6AF width ruling: at 87 columns with 6 roles and a 20-char person
    id the grid never wraps — no painted line exceeds the width, the id
    truncates with the ellipsis at the fixed 12-cell column, every role
    header is present, and the band stays its fixed height."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, SUBJECT)
    create_registry(
        tmp_path, person=SUBJECT[0], name=SUBJECT[1], email=SUBJECT[2],
        roles=ROLES_SIX, now=T0,
    )
    _add_person(tmp_path, (LONG_ID, "Long", "long@example.invalid"), T1)

    app = MapperApp(tmp_path)
    async with app.run_test(size=(87, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        body = _render_text(screen, "roles-body", 87)
        band = _render_text(screen, "roles-band", 87)
        status = _plain(screen, "roles-status")
        band_height = screen.query_one("#roles-band", Static).size.height

    assert all(len(line) <= 87 for line in body.splitlines()), body
    assert all(len(line) <= 87 for line in band.splitlines()), band
    assert all(len(line) <= 87 for line in status.splitlines()), status
    # the id truncates with the ellipsis at the fixed 12-cell column
    expected_id = darkside.fit(LONG_ID, 12).rstrip()
    assert expected_id in body, body
    assert LONG_ID not in body, body
    long_row = _row(body, expected_id)
    assert GLYPH_NOT_HELD in long_row, long_row
    # all six role headers paint
    for role in ROLES_SIX:
        assert role in body, (role, body)
    # the band is its fixed height and the head hash is 12 hex + the ellipsis
    assert band_height == 5, band_height
    assert "head " in band and "\u2026" in band, band


async def test_rh6af_no_event_ledger_below_the_matrix(tmp_path):
    """RH6AF drift ruling: the chain event ledger is gone from below the
    matrix (variant C's chain view was never adopted — NOTES.md), while
    LLR-RH.8.1's verbatim genesis copy stays on screen."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, SUBJECT)
    _seed_team(tmp_path, env)

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        body = _render_text(screen, "roles-body", 118)

    # the ledger's signature — one line per chain event — paints nowhere
    assert re.search(r"^#\d+ ", body, re.M) is None, body
    assert "grant reviewer-2 +req-reviewer by subject" not in body, body
    # LLR-RH.8.1: the genesis copy stays, verbatim
    assert "genesis \u2014 declared at registry creation" in body, body


async def test_rh6af_propose_writer_oserror_notifies_exception_type(
        tmp_path, monkeypatch):
    """RH6AF: a writer `OSError` from the core's pending path is caught and
    named by exception TYPE in a markup-free error notification — nothing is
    written, and the message paints no path the OS error text could embed."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, REVIEWER2)  # a non-admin: the pending path
    _seed_team(tmp_path, env)

    def _boom(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(chain_module, "_write_pending", _boom)  # noqa: SLF001

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        before = _roles_sha(tmp_path)
        # cursor (0,0) = subject x admin: held -> a pending revoke proposal,
        # which is exactly the writer the monkeypatch raises under
        await _press(pilot, "space")
        await pilot.pause()
        notifications = list(app._notifications)  # noqa: SLF001
        hint = screen.query_one(HintLine).text

    assert _roles_sha(tmp_path) == before, "roles.yml moved on a failed write"
    assert _pending_files(tmp_path) == [], _pending_files(tmp_path)
    assert len(notifications) == 1, notifications
    notification = notifications[0]
    assert notification.message == "could not propose the change: OSError"
    assert notification.severity == "error"
    assert notification.markup is False
    assert "proposed" not in hint, hint


# ---------------------------------------------------------------------------
# AT-082 — admin a/r pending resolution (LLR-RH.8.6, increment RH6b)
# ---------------------------------------------------------------------------

T4 = "2026-10-11T09:04:00Z"
# after any wall-clock chain event the screen's own resolutions land with —
# fixed-time fixture writes that must postdate them
T_LATE = "2099-01-01T00:00:00Z"


def _open_request(tmp_path: Path, role: str):
    """The single open pending grant of *role* for reviewer-2 on disk — its
    file name and digest."""
    requests = [
        request
        for request in list_pending(tmp_path).requests
        if request.person == "reviewer-2" and request.action == "grant"
        and request.role == role
    ]
    assert len(requests) == 1, requests
    return requests[0]


async def test_at_082_admin_resolves_pending_with_a_and_r(tmp_path):
    """LLR-RH.8.6: `a` approves the pending change under the cursor — one
    chain event referencing the request's sha256 (the pending file stays);
    `r` rejects with an empty `resolution` event, glyph cleared; a
    non-admin's `a` paints exactly "a is unavailable (needs an admin)"; the
    resolutions survive an app restart."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, SUBJECT)
    _seed_team(tmp_path, env)
    # reviewer-2 (non-admin) proposes +safety-lead for himself: it pends
    assert propose(tmp_path, requester="reviewer-2", action="grant",
                    person="reviewer-2", role="safety-lead", now=T3) is not None
    request = _open_request(tmp_path, "safety-lead")
    pending_name = request.name
    files_before = {p.name for p in _pending_files(tmp_path)}

    # -- arm 1: the admin's `a` lands the change as ONE chain event ----------
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        events_before = len(_read_docs(tmp_path))
        await _goto(pilot, 1, 2)  # reviewer-2 x safety-lead
        await _press(pilot, "a")
        events_after = len(_read_docs(tmp_path))
        body = _render_text(screen, "roles-body", 118)
        band = _render_text(screen, "roles-band", 118)
        hint = screen.query_one(HintLine).text
    assert events_after == events_before + 1, (events_before, events_after)
    landed = _read_docs(tmp_path)[-1]
    assert landed["action"] == "grant"
    assert landed["person"] == "reviewer-2" and landed["role"] == "safety-lead"
    assert landed["requested_by"] == "reviewer-2" and landed["approved_by"] == "subject"
    assert landed["request_hash"] == request.digest
    # the pending file stays on disk; the resolution is derived (R6)
    assert {p.name for p in _pending_files(tmp_path)} == files_before
    reviewer_row = _row(body, "reviewer-2")
    assert reviewer_row.count(GLYPH_IN_FORCE) == 2, reviewer_row
    assert GLYPH_PENDING_ADD not in reviewer_row, reviewer_row
    assert "pending 0" in band, band
    assert hint == "approved: reviewer-2 +safety-lead (requested by reviewer-2)", hint

    # -- arm 2: a second pending, rejected with `r` ----------------------------
    # the approve above landed with wall-clock time; this request must postdate it
    assert propose(tmp_path, requester="reviewer-2", action="grant",
                   person="reviewer-2", role="board", now=T_LATE) is not None
    request2 = _open_request(tmp_path, "board")
    assert request2.name != pending_name
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        events_before = len(_read_docs(tmp_path))
        await _goto(pilot, 1, 3)  # reviewer-2 x board
        await _press(pilot, "r")
        events_after = len(_read_docs(tmp_path))
        body = _render_text(screen, "roles-body", 118)
        hint = screen.query_one(HintLine).text
    assert events_after == events_before + 1, (events_before, events_after)
    landed = _read_docs(tmp_path)[-1]
    assert landed["action"] == "resolution"
    assert landed["person"] == "" and landed["role"] == ""
    assert landed["request_hash"] == request2.digest
    reviewer_row = _row(body, "reviewer-2")
    assert GLYPH_PENDING_ADD not in reviewer_row, reviewer_row
    assert reviewer_row.count(GLYPH_IN_FORCE) == 2, reviewer_row
    assert GLYPH_NOT_HELD in reviewer_row, reviewer_row
    assert hint == "rejected: reviewer-2 +board (requested by reviewer-2)", hint

    # -- arm 3: a non-admin's `a` paints the exact unavailability message -----
    _set_identity(tmp_path, env, REVIEWER2)
    sha_before = _roles_sha(tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        await _goto(pilot, 1, 2)
        await _press(pilot, "a")
        hint = screen.query_one(HintLine).text
        notifications = list(app._notifications)  # noqa: SLF001
    assert hint == "a is unavailable (needs an admin)", hint
    assert _roles_sha(tmp_path) == sha_before, "a non-admin a/r wrote the chain"
    assert notifications == [], notifications

    # -- arm 4: restart — both resolutions are still derived from the chain ---
    _set_identity(tmp_path, env, SUBJECT)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        body = _render_text(screen, "roles-body", 118)
        band = _render_text(screen, "roles-band", 118)
    reviewer_row = _row(body, "reviewer-2")
    # approved: safety-lead in force; rejected: board not held, nothing pends
    assert reviewer_row.count(GLYPH_IN_FORCE) == 2, reviewer_row
    assert GLYPH_PENDING_ADD not in reviewer_row, reviewer_row
    assert GLYPH_NOT_HELD in reviewer_row, reviewer_row
    assert "pending 0" in band, band
    assert {p.name for p in _pending_files(tmp_path)} == {pending_name, request2.name}


# ---------------------------------------------------------------------------
# RH6b — boundary nodes: own request, non-admin inert, tampered inert,
# double resolution named, OSError arm
# ---------------------------------------------------------------------------


async def test_rh6b_admin_resolving_own_request_is_refused_and_named(tmp_path):
    """LLR-RH.8.6 boundary: the core refuses one's own request; the screen
    paints the core's named refusal in a markup-free notification and writes
    nothing."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, SUBJECT)
    _seed_team(tmp_path, env)
    # the admin's own change stays pending (nobody applies to themselves)
    assert propose(tmp_path, requester="subject", action="grant",
                    person="subject", role="board", now=T3) is not None

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        await _open_roles(app, pilot)
        events_before = len(_read_docs(tmp_path))
        sha_before = _roles_sha(tmp_path)
        await _goto(pilot, 0, 3)  # subject x board: their own pending change
        await _press(pilot, "a")
        await pilot.pause()
        notifications_a = list(app._notifications)  # noqa: SLF001
        hint_a = app.screen.query_one(HintLine).text
        await _press(pilot, "r")
        await pilot.pause()
        notifications_r = list(app._notifications)  # noqa: SLF001
        hint_r = app.screen.query_one(HintLine).text

    assert len(_read_docs(tmp_path)) == events_before, "own request resolved"
    assert _roles_sha(tmp_path) == sha_before
    assert len(notifications_a) == 1
    assert len(notifications_r) == 2, notifications_r
    # the toast names the refusal by TYPE (INC9-SEC-F1); the named refusal
    # itself paints verbatim on the hint line
    assert notifications_a[0].message == "could not approve the request: ValidationError"
    assert notifications_a[0].severity == "error"
    assert notifications_a[0].markup is False
    assert "cannot approve their own request" in hint_a, hint_a
    assert notifications_r[-1].message == "could not reject the request: ValidationError"
    assert notifications_r[-1].markup is False
    assert "cannot reject their own request" in hint_r, hint_r


async def test_rh6b_non_admin_resolution_keys_inert(tmp_path):
    """LLR-RH.8.6 invalid arm: a non-admin's `a` AND `r` write nothing and
    show the unavailability message (byte-exact for `a` per R6)."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, REVIEWER2)  # the viewer is a non-admin
    _seed_team(tmp_path, env)
    assert propose(tmp_path, requester="reviewer-2", action="grant",
                   person="reviewer-2", role="safety-lead", now=T3) is not None

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        events_before = len(_read_docs(tmp_path))
        sha_before = _roles_sha(tmp_path)
        await _goto(pilot, 1, 2)
        await _press(pilot, "a")
        hint_a = screen.query_one(HintLine).text
        await _press(pilot, "r")
        hint_r = screen.query_one(HintLine).text
        body = _render_text(screen, "roles-body", 118)

    assert hint_a == "a is unavailable (needs an admin)", hint_a
    assert hint_r == "r is unavailable (needs an admin)", hint_r
    assert len(_read_docs(tmp_path)) == events_before
    assert _roles_sha(tmp_path) == sha_before
    # the pending glyph stays — nothing resolved
    assert GLYPH_PENDING_ADD in _row(body, "reviewer-2"), body


async def test_rh6b_tampered_chain_resolution_keys_inert(tmp_path):
    """LLR-RH.8.6 read-only arm: on a tampered chain `a` is inert, paints the
    read-only message and writes nothing."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, SUBJECT)
    _seed_team(tmp_path, env)
    assert propose(tmp_path, requester="reviewer-2", action="grant",
                   person="reviewer-2", role="safety-lead", now=T3) is not None
    # the hand edit: reviewer-2's grant becomes an admin grant, hashes stale
    docs = _read_docs(tmp_path)
    docs[2]["role"] = "admin"
    _write_docs(tmp_path, docs)
    assert verify_chain(tmp_path).status == "config changed without approval"

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        before = _roles_sha(tmp_path)
        events_before = len(_read_docs(tmp_path))
        await _goto(pilot, 1, 2)
        await _press(pilot, "a")
        after = _roles_sha(tmp_path)
        hint = screen.query_one(HintLine).text

    assert before == after, "a wrote to a tampered chain"
    assert len(_read_docs(tmp_path)) == events_before
    assert "read-only" in hint, hint


async def test_rh6b_double_resolution_refusal_is_named(tmp_path):
    """LLR-RH.8.6 + H1: a request the verified chain ALREADY references is
    refused by the core; the screen paints the named refusal and appends
    nothing.  The fixture crafts a chain event that references the request's
    digest without applying it (a mismatched grant), so the request still
    derives `pending` on screen while the chain already references it."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, SUBJECT)
    _seed_team(tmp_path, env)
    assert propose(tmp_path, requester="reviewer-2", action="grant",
                   person="reviewer-2", role="safety-lead", now=T3) is not None
    request = _open_request(tmp_path, "safety-lead")
    docs = _read_docs(tmp_path)
    head = verify_chain(tmp_path).events[-1].this_hash
    # a grant of a role reviewer-2 ALREADY holds, carrying the pending
    # request's digest: derivation keeps the request `pending` (person/role
    # mismatch), the chain already references it — the H1 double-resolution
    # guard is exactly what a second resolution attempt must hit
    body = {
        "seq": 4,
        "time": T4,
        "requested_by": "reviewer-2",
        "approved_by": "subject",
        "action": "grant",
        "person": "reviewer-2",
        "role": "req-reviewer",
        "note": "references the open request without applying it",
        "roles_seq": 3,
        "roles_hash": head,
        "prev_hash": head,
        "request_hash": request.digest,
    }
    body["this_hash"] = chain_hash(head, body)
    _write_docs(tmp_path, [*docs, body])
    report = verify_chain(tmp_path)
    assert report.ok, report.status
    assert _open_request(tmp_path, "safety-lead").digest == request.digest  # still pending

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        await _open_roles(app, pilot)
        events_before = len(_read_docs(tmp_path))
        await _goto(pilot, 1, 2)  # reviewer-2 x safety-lead: the open request
        await _press(pilot, "a")
        await pilot.pause()
        notifications = list(app._notifications)  # noqa: SLF001
        hint = app.screen.query_one(HintLine).text

    assert len(_read_docs(tmp_path)) == events_before, "a double resolution landed"
    assert len(notifications) == 1, notifications
    assert notifications[0].message == "could not approve the request: ValidationError"
    assert notifications[0].severity == "error"
    assert notifications[0].markup is False
    # the named refusal paints verbatim on the hint line (a Text sink)
    assert "request already resolved" in hint, hint


async def test_rh6b_resolution_writer_oserror_notifies_exception_type(
        tmp_path, monkeypatch):
    """RH6b: a writer `OSError` from the core's resolution path is caught and
    named by exception TYPE in a markup-free notification — nothing is
    written."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, SUBJECT)
    _seed_team(tmp_path, env)
    assert propose(tmp_path, requester="reviewer-2", action="grant",
                   person="reviewer-2", role="safety-lead", now=T3) is not None

    def _boom(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(chain_module, "_append_event", _boom)  # noqa: SLF001

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        events_before = len(_read_docs(tmp_path))
        await _goto(pilot, 1, 2)
        await _press(pilot, "a")
        await pilot.pause()
        notifications = list(app._notifications)  # noqa: SLF001
        hint = screen.query_one(HintLine).text

    assert len(_read_docs(tmp_path)) == events_before, "the failed write landed"
    assert len(notifications) == 1, notifications
    notification = notifications[0]
    assert notification.message == "could not approve the request: OSError"
    assert notification.severity == "error"
    assert notification.markup is False
    assert "approved" not in hint, hint


# ---------------------------------------------------------------------------
# RHFIX6B — code-review follow-up (APPROVE-WITH-NITS): several-pending
# refusal, stale-authority reload at keypress, success hints name the
# request, non-pending cursor cell
# ---------------------------------------------------------------------------

_SEVERAL_HINT = (
    "several pending requests on this cell \u2014 "
    "resolve them from the core (B-126 follow-up)"
)
# a fixture write that must postdate the mid-session admin grant (T_LATE)
T_LATER = "2099-01-01T00:01:00Z"
# a chain event time AFTER the seed (T4) but BEFORE wall clock, for
# mid-session on-disk grants the screen itself then resolves
T5 = "2026-10-11T09:05:00Z"


async def test_rhfix6b_several_pending_on_one_cell_refuses_a_and_r(tmp_path):
    """RHFIX6B (MED): a cell with SEVERAL open pending requests must not be
    resolved by silently picking the oldest — `a` AND `r` refuse with the
    named hint and write nothing (the chain bytes are unchanged)."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, SUBJECT)
    _seed_team(tmp_path, env)
    # TWO open requests on the SAME cell: same person/role/action, two times
    assert propose(tmp_path, requester="reviewer-2", action="grant",
                    person="reviewer-2", role="safety-lead", now=T3) is not None
    assert propose(tmp_path, requester="reviewer-2", action="grant",
                    person="reviewer-2", role="safety-lead", now=T_LATE) is not None

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        events_before = len(_read_docs(tmp_path))
        sha_before = _roles_sha(tmp_path)
        await _goto(pilot, 1, 2)  # reviewer-2 x safety-lead: two open requests
        await _press(pilot, "a")
        hint_a = screen.query_one(HintLine).text
        await _press(pilot, "r")
        hint_r = screen.query_one(HintLine).text
        notifications = list(app._notifications)  # noqa: SLF001

    assert hint_a == _SEVERAL_HINT, hint_a
    assert hint_r == _SEVERAL_HINT, hint_r
    assert len(_read_docs(tmp_path)) == events_before, "a/r wrote the chain"
    assert _roles_sha(tmp_path) == sha_before, "a/r moved roles.yml"
    assert notifications == [], notifications


async def test_rhfix6b_admin_revoked_on_disk_refuses_a_at_keypress(tmp_path):
    """RHFIX6B (LOW, stale authority arm 1): the admin pre-filter reflects
    DISK at keypress time — a viewer who was an admin at mount but was
    revoked on disk mid-session is refused by the named hint and nothing is
    written."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, SUBJECT)
    _seed_team(tmp_path, env)
    # a second admin (ana), so ana can revoke the viewer's admin on disk
    _add_person(tmp_path, ("ana", "Ana", "ana@example.invalid"), T3)
    assert propose(tmp_path, requester="subject", action="grant",
                   person="ana", role="admin", now=T4) is None
    # a pending request on the cursor cell (requested by someone else)
    assert propose(tmp_path, requester="reviewer-2", action="grant",
                    person="reviewer-2", role="safety-lead", now=T_LATE) is not None

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        # the viewer IS an admin at mount — now revoke them on disk, mid-session
        assert propose(tmp_path, requester="ana", action="revoke",
                       person="subject", role="admin", now=T_LATER) is None
        events_before = len(_read_docs(tmp_path))
        sha_before = _roles_sha(tmp_path)
        await _goto(pilot, 1, 2)  # reviewer-2 x safety-lead
        await _press(pilot, "a")
        hint = screen.query_one(HintLine).text
        notifications = list(app._notifications)  # noqa: SLF001

    assert hint == "a is unavailable (needs an admin)", hint
    assert len(_read_docs(tmp_path)) == events_before, "a resolved after a disk revoke"
    assert _roles_sha(tmp_path) == sha_before
    assert notifications == [], notifications


async def test_rhfix6b_admin_granted_on_disk_allows_a_at_keypress(tmp_path):
    """RHFIX6B (LOW, stale authority arm 2): a viewer who was NOT an admin at
    mount but was granted admin on disk mid-session resolves with `a`
    in place — the approval lands as one chain event and the success hint
    names the request."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, REVIEWER2)  # the viewer is a non-admin at mount
    _seed_team(tmp_path, env)
    _add_person(tmp_path, ("ana", "Ana", "ana@example.invalid"), T3)
    # ana's own change pends — requested by ana, so the viewer may approve it
    assert propose(tmp_path, requester="ana", action="grant",
                    person="ana", role="safety-lead", now=T4) is not None

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        # non-admin at mount — grant the viewer admin on disk, mid-session
        # (a chain time before wall clock: the screen's own approval must
        # still postdate it)
        assert propose(tmp_path, requester="subject", action="grant",
                       person="reviewer-2", role="admin", now=T5) is None
        events_before = len(_read_docs(tmp_path))
        await _goto(pilot, 2, 2)  # ana x safety-lead
        await _press(pilot, "a")
        events_after = len(_read_docs(tmp_path))
        hint = screen.query_one(HintLine).text
        notifications = list(app._notifications)  # noqa: SLF001

    assert events_after == events_before + 1, (events_before, events_after,
                                               hint, notifications)
    landed = _read_docs(tmp_path)[-1]
    assert landed["action"] == "grant"
    assert landed["person"] == "ana" and landed["role"] == "safety-lead"
    assert landed["requested_by"] == "ana" and landed["approved_by"] == "reviewer-2"
    assert hint == "approved: ana +safety-lead (requested by ana)", hint
    assert notifications == [], notifications


async def test_rhfix6b_cursor_on_non_pending_cell_shows_no_pending_hint(tmp_path):
    """RHFIX6B (LOW): the cursor on a cell with NO pending request paints the
    named no-pending hint and writes nothing."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, SUBJECT)
    _seed_team(tmp_path, env)

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_roles(app, pilot)
        events_before = len(_read_docs(tmp_path))
        sha_before = _roles_sha(tmp_path)
        await _goto(pilot, 1, 1)  # reviewer-2 x req-reviewer: held, nothing pending
        await _press(pilot, "a")
        hint = screen.query_one(HintLine).text

    assert hint == "no pending change under the cursor", hint
    assert len(_read_docs(tmp_path)) == events_before
    assert _roles_sha(tmp_path) == sha_before
