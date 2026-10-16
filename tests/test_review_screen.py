"""HLR-RS.1..5 — the ReqHarness REVIEW / SIGNING screen (variant A, B-134):
AT-090…AT-107 of batch `2026-10-15-review-screen-batch` (increment RS2).

Every drive is `MapperApp(tmp_path)` + `run_test(size=(W, 34))` + real
`pilot.press` keys, asserted on the PAINTED frame (C-32).  Helpers are reused
from `tests/test_roles_screen.py` (`_init_repo`, `_set_identity`, `_seed_team`,
`_add_person`, `_plain`, `_render_text`), `tests/test_fixes_roles_thread.py`
(`_Gate`, `_install_gate`, `_settle`, `_until`, `_painted`),
`tests/test_reqharness_registry.py` (`_record_review`, `_digests`, `_row`,
`CANON_HEADER`, `HLR_FIELDS`) and `tests/test_draft_save.py` (`_press`).
"""
from __future__ import annotations

import ast
import asyncio
import threading
from types import SimpleNamespace
from pathlib import Path

import pytest
import yaml
from textual.screen import Screen
from textual.worker import WorkerState

from mapper import darkside
from mapper.app import HomeScreen, MapperApp
import mapper.reqharness.identity as identity_module
from mapper.reqharness import derive, release as release_mod, reviews
from mapper.reqharness.chain import append_policy, propose, verify_chain
from mapper.reqharness.config import (
    load_documents,
)
# The screen's own `signing` binding is patched, so this file never imports
# `mapper.reqharness.signing` (LLR-RS.2.4 allowlist in test_reqharness_signing).
from mapper.screens.review import signing
from mapper.screens.review import (
    _discover,
    _elide_middle,
    _load,
    ReviewList,
    ReviewScreen,
    _hint_text,
    _list_row_text,
    _Row,
)
from mapper.widgets.chrome import HintLine, KeyBar
from tests.test_draft_save import _press
from tests.test_fixes_roles_thread import _Gate, _painted, _settle, _until
from tests.test_reqharness_registry import (
    CANON_HEADER,
    T3,
    T4,
    _record_review,
    _row,
)
from tests.test_roles_screen import (
    REVIEWER2,
    _add_person,
    _init_repo,
    _plain,
    _render_text,
    _seed_team,
    _set_identity,
)

WIDTHS = [118, 87]
SIZE = (118, 34)

ANA = ("ana", "Ana", "ana@example.invalid")
QA1 = ("qa-1", "Qa One", "qa-1@example.invalid")

# The canon objects and their statements (the mixed state, §9.1).
STATEMENTS = {
    "HLR-RH.1": "review registry",
    "HLR-RH.2": "digests and baselines",
    "HLR-RH.4": "immutable store",
    "HLR-RH.7": "release rules",
    "LLR-RH.7.1": "verdict strings",
    "LLR-RH.8.1": "matrix glyph set",
    "LLR-RH.8.2": "coverage walk",
}

MIXED_CANON = CANON_HEADER + "".join(
    _row(oid, STATEMENTS[oid], "active") for oid in STATEMENTS
) + _row("LLR-RH.9.2", "superseded", "withdrawn (deferred)")


def _fields(statement: str, status: str = "active") -> dict:
    return {"statement": statement, "status": status}


def _config_doc(root: Path):
    path = root / "reqharness" / "config.yml"
    (document,) = load_documents(path.read_text(encoding="utf-8"), where="reqharness/config.yml")
    return path, document


def _set_authors(root: Path, authors: dict) -> None:
    path, document = _config_doc(root)
    document["authors"] = authors
    path.write_text(
        yaml.safe_dump(document, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
        newline="\n",
    )
    append_policy(root, approved_by="subject", note="declare authors", now=T3)


def _write_canon(root: Path, text: str) -> None:
    (root / "REQUIREMENTS.md").write_text(text, encoding="utf-8", newline="\n")


def _seed_reviewer(tmp_path: Path, viewer=REVIEWER2, *, authors=None):
    """git init + identity=viewer + subject genesis + reviewer-2/ana/qa-1."""
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, viewer)
    _seed_team(tmp_path, env)
    _add_person(tmp_path, ANA, T3)
    _add_person(tmp_path, QA1, T3)
    propose(tmp_path, requester="subject", action="grant", person="ana", role="req-reviewer", now=T3)
    if authors is not None:
        _set_authors(tmp_path, authors)
    return env


def _mixed(tmp_path: Path, viewer=REVIEWER2):
    """The §9.1 mixed registry: 2 reviewed, 2 changed, 2 pre-reviewed, 1 not
    reviewed, 1 retired, with an unentitled review and a model review."""
    env = _seed_reviewer(tmp_path, viewer=viewer)
    _write_canon(tmp_path, MIXED_CANON)
    _record_review(tmp_path, "HLR-RH.1", _fields("review registry"), reviewer="ana", now=T4)
    _record_review(tmp_path, "HLR-RH.2", _fields("old digests"), reviewer="ana", now=T4)
    _record_review(tmp_path, "HLR-RH.4", _fields("immutable store"), reviewer="ana", now=T4)
    _record_review(tmp_path, "HLR-RH.7", _fields("release rules"), reviewer="kimi-code", kind="model", now=T4)
    _record_review(tmp_path, "LLR-RH.7.1", _fields("verdict strings"), reviewer="qa-1", now=T4)
    _record_review(tmp_path, "LLR-RH.8.1", _fields("old glyphs"), reviewer="reviewer-2", now=T4)
    return env


async def _open_review(app: MapperApp, pilot) -> ReviewScreen:
    await _press(pilot, "v")
    screen = app.screen
    assert isinstance(screen, ReviewScreen), type(screen)
    await asyncio.wait_for(app.workers.wait_for_complete(), timeout=60)
    await pilot.pause()
    return screen


def _frame(screen) -> str:
    """The composited painted frame — every visible character, per row."""
    return "\n".join(
        "".join(seg.text for seg in strip)
        for strip in screen._compositor.render_strips()  # noqa: SLF001
    )


def _review_files(root: Path) -> list[Path]:
    directory = root / "reqharness" / "reviews"
    return sorted(directory.glob("*.yml")) if directory.is_dir() else []


def _derive_states(root: Path, canon_text: str):
    from mapper.reqharness.config import load_config

    config = load_config(root)
    report = verify_chain(root)
    scan = reviews.load_reviews(root)
    canon, _ = derive.parse_canon(canon_text)
    return derive.derive_states(canon, scan, report, config)


# ---------------------------------------------------------------------------
# AT-090 — home door opens the screen; the frame paints the registry
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("width", WIDTHS)
async def test_at_090_review_screen_opens_from_home_and_paints_the_registry(tmp_path, width):
    _mixed(tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        await pilot.pause()
        assert isinstance(app.screen, HomeScreen)
        door = app.screen._empty_text().plain  # noqa: SLF001
        assert "v review" in door, door
        screen = await _open_review(app, pilot)
        frame = _frame(screen)
        status = _plain(screen, "review-status")
        band = _render_text(screen, "review-band", width)

    assert "\u2713 verified" in status, status
    for oid in STATEMENTS:
        assert oid in frame, (oid, frame)
    assert "LLR-RH.9.2" in frame, frame
    assert "not verifiable" not in frame, frame
    # M-RS1: every listed id carries the state word `derive` computed for it
    # (read, never recomputed in the screen), on the id's own list row.
    expected = _derive_states(tmp_path, MIXED_CANON).states
    assert len(set(expected.values())) >= 4, expected
    lines = frame.splitlines()
    for oid, word in expected.items():
        assert any(oid in ln and word in ln for ln in lines), (oid, word, frame)
    assert "release readiness" in band, band


# ---------------------------------------------------------------------------
# AT-091 — the "needs action" preset lists only the open states
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("width", WIDTHS)
async def test_at_091_needs_action_filter_preset_lists_only_open_objects(tmp_path, width):
    _mixed(tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "4")  # all -> needs action
        frame = _frame(screen)

    # the three open states are present; reviewed and retired are not
    assert "changed \u00b7 review" in frame, frame
    assert "pre-reviewed" in frame, frame
    assert "not reviewed" in frame, frame
    # reviewed objects (HLR-RH.1, HLR-RH.4) and retired (LLR-RH.9.2) are absent
    assert "HLR-RH.1" not in frame, frame
    assert "HLR-RH.4" not in frame, frame
    assert "LLR-RH.9.2" not in frame, frame
    # the open object ids are present
    for oid in ("HLR-RH.2", "HLR-RH.7", "LLR-RH.7.1", "LLR-RH.8.1", "LLR-RH.8.2"):
        assert oid in frame, (oid, frame)


# ---------------------------------------------------------------------------
# AT-092 — the detail pane shows history, digests, model review, badge
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("width", WIDTHS)
async def test_at_092_detail_pane_shows_history_digest_verdicts_and_informative_badge(tmp_path, width):
    _seed_reviewer(tmp_path)
    canon = CANON_HEADER + (
        _row("HLR-RH.1", "review registry", "active", "first rationale")
        + _row("HLR-RH.2", "digests and baselines", "active")
    )
    _write_canon(tmp_path, canon)
    # a stale review (digest ✗) and a model review on the same digest
    _record_review(tmp_path, "HLR-RH.1", _fields("old registry"), reviewer="ana", now=T4)
    _record_review(tmp_path, "HLR-RH.1", _fields("review registry"), reviewer="kimi-code", kind="model", now=T4)

    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        detail = _plain(screen, "review-detail")
        band = _render_text(screen, "review-band", width)

    assert "review history" in detail, detail
    assert "(human)" in detail and "(model)" in detail, detail
    assert "\u2717 stale \u2014 content changed" in detail, detail
    assert "\u2713 matches" in detail, detail
    assert "head " in detail, detail
    verdict = _derive_states(tmp_path, canon)
    from mapper.reqharness.config import load_config
    from mapper.reqharness import release as release_mod

    config = load_config(tmp_path)
    expected = release_mod.evaluate(config, verify_chain(tmp_path), verdict)
    assert expected.text in band, (expected.text, band)


# ---------------------------------------------------------------------------
# AT-093 — `b` shows the digest + head; `enter` signs through `sign_review`
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("width", WIDTHS)
async def test_at_093_b_shows_digest_and_head_and_enter_signs_through_sign_review(tmp_path, width):
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))
    from mapper.reqharness.config import load_config
    from mapper.reqharness import derive as derive_mod

    config = load_config(tmp_path)
    head = verify_chain(tmp_path).head
    obj = next(c for c in derive_mod.load_canon(tmp_path)[0] if c.id == "HLR-RH.1")
    cls = next(c for c in config.classes if c.id == obj.class_id)
    normative, _ = derive_mod.object_digests(cls, obj.fields)

    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "b")
        hint = _painted(screen, HintLine)
        assert normative[:8] in hint, hint  # the digest is always shown in full
        # the head hash is shown, but yields hex down to 1 at 87 (6 at 118) to
        # keep the short object id intact (U5): assert the first hex, which both
        # widths paint in the "head" position.
        assert f"head {head[1][:1]}" in hint, hint
        await _press(pilot, "enter")
        await asyncio.wait_for(app.workers.wait_for_complete(), timeout=60)
        await pilot.pause()

    files = _review_files(tmp_path)
    assert len(files) == 1, files
    result = _derive_states(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))
    assert result.states["HLR-RH.1"] == derive.STATE_REVIEWED
    by_name = {e.name: e for e in reviews.load_reviews(tmp_path).events}
    [event] = by_name.values()
    assert event.kind == "human" and event.verdict == "reviewed" and event.note == ""


# ---------------------------------------------------------------------------
# AT-098 — a cold `enter` writes nothing and changes no painted surface
# ---------------------------------------------------------------------------


async def test_at_098_cold_enter_does_nothing(tmp_path):
    _mixed(tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        before = _frame(screen)
        before_count = len(_review_files(tmp_path))
        await _press(pilot, "enter")
        after = _frame(screen)

    assert len(_review_files(tmp_path)) == before_count
    assert before == after


# ---------------------------------------------------------------------------
# AT-094 — `b` refuses with the reason (no role, retired, undeclared, no
# git identity, no registry)
# ---------------------------------------------------------------------------


async def test_at_094_b_refuses_when_the_viewer_lacks_the_role_or_the_object_is_retired(tmp_path):
    # arm 1: the viewer (reviewer-2) lacks no role — reviewer-2 holds
    # req-reviewer, so sign a retired object instead: a viewer without the
    # safety-lead role on an object whose class demands it is built by
    # planting an object the viewer cannot cover.  Here: reviewer-2 holds
    # req-reviewer, an HLR object is covered — so instead assert the retired
    # object and the no-role case with a fresh viewer (qa-1).
    _seed_reviewer(tmp_path, viewer=QA1)  # qa-1 holds no req-reviewer
    _write_canon(
        tmp_path,
        CANON_HEADER + _row("HLR-RH.1", "review registry", "active")
        + _row("LLR-RH.9.2", "superseded", "withdrawn (deferred)"),
    )
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "b")
        hint = _painted(screen, HintLine)
        assert "does not hold the req-reviewer role" in hint, hint
        assert _review_files(tmp_path) == []
        # move to the retired object
        await _press(pilot, "down")
        await _press(pilot, "b")
        hint2 = _painted(screen, HintLine)
    assert "is retired" in hint2, hint2
    assert _review_files(tmp_path) == []


async def test_at_094_undeclared_viewer_no_git_identity_and_no_registry(tmp_path):
    # undeclared viewer: a git identity matching no declared person
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, ("mallory", "Mallory", "mallory@example.invalid"))
    _seed_team(tmp_path, env)
    _write_canon(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "b")
        hint = _painted(screen, HintLine)
    assert "is not a declared person" in hint, hint

    # no git identity: a registry with no user.email
    noid = tmp_path / "noid"
    env2 = _init_repo(noid)
    _seed_team(noid, env2)
    _write_canon(noid, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))
    app2 = MapperApp(noid)
    async with app2.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen2 = await _open_review(app2, pilot)
        await _press(pilot, "b")
        hint2 = _painted(screen2, HintLine)
    assert "is not a declared person" in hint2, hint2

    # no registry: a git repo with no reqharness/
    noreg = tmp_path / "noreg"
    env3 = _init_repo(noreg)
    _set_identity(noreg, env3, REVIEWER2)
    app3 = MapperApp(noreg)
    async with app3.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen3 = await _open_review(app3, pilot)
        await _press(pilot, "b")
        hint3 = _painted(screen3, HintLine)
    assert "no registry yet" in hint3, hint3


# ---------------------------------------------------------------------------
# AT-095 — a tampered chain is read-only with the reason
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("width", WIDTHS)
async def test_at_095_tampered_or_forked_chain_is_read_only_with_the_reason(tmp_path, width):
    _mixed(tmp_path)
    # hand-edit the grant: reviewer-2's grant becomes an admin grant
    from tests.test_roles_screen import _read_docs, _write_docs

    docs = _read_docs(tmp_path)
    docs[2]["role"] = "admin"
    _write_docs(tmp_path, docs)
    assert verify_chain(tmp_path).status == "config changed without approval"

    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        frame = _frame(screen)
        status = _plain(screen, "review-status")
        band = _render_text(screen, "review-band", width)
        before = len(_review_files(tmp_path))
        await _press(pilot, "b")
        hint = _painted(screen, HintLine)

    assert "config changed without approval" in status, status
    assert "not verifiable" in frame, frame
    assert "release readiness \u2014 BLOCKED" in band, band
    assert len(_review_files(tmp_path)) == before
    assert "cannot sign: registry not verifiable" in hint, hint


# ---------------------------------------------------------------------------
# AT-096 — a hostile registry paints literally, no ESC byte, no markup span
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("width", WIDTHS)
async def test_at_096_screen_paints_file_derived_text_through_text_sinks_only(tmp_path, width):
    esc = chr(0x1B)
    rlo = chr(0x202E)
    zwsp = chr(0x200B)
    nel = chr(0x85)
    cjk = chr(0x4E2D)
    combining = "e" + chr(0x301)
    # the object id carries the non-whitespace payload (NEL would break the
    # canon row's `\S+` id match); the reviewer name carries the full payload.
    hostile_id = "HLR-EVIL" + esc + rlo + zwsp + cjk + combining + "[bold]x[/]"
    hostile_reviewer = "eve" + nel + rlo + esc + "[bold]x[/]"
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row(hostile_id, "review registry", "active"))
    _record_review(tmp_path, hostile_id, _fields("review registry"), reviewer=hostile_reviewer, now=T4)

    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        frame = _frame(screen)
        detail = _plain(screen, "review-detail")

    assert esc not in frame, repr(frame)
    assert "[bold]x[/]" in frame, frame  # markup brackets paint literally
    assert "\ufffd" in frame, frame  # control bytes coerced to the replacement char
    # M-RS11: the detail pane is a Text sink too -- a markup `Static(str)` there
    # would eat the brackets while the list row still shows them.  Read the
    # PAINTED columns right of the list (the detail pane is 46 wide), not the
    # widget's stored content.
    pane = [line[width - 46 :] for line in frame.splitlines()]
    assert any("[bold]x[/]" in line for line in pane), pane
    assert esc not in detail, repr(detail)


async def test_q2_armed_hint_carries_no_raw_control_or_markup(tmp_path):
    """The armed hint (a file-derived object id, elided) coerces the control
    payload and paints the markup brackets literally — no raw ESC/RLO/ZWSP, no
    markup span.  NEL (U+0085) is a line separator and would break the canon
    row's `\\S+` id match, so it cannot ride the object id (AT-096's
    reviewer-name payload covers it through the same `darkside.plain` path)."""
    esc = chr(0x1B)
    rlo = chr(0x202E)
    zwsp = chr(0x200B)
    # long enough to elide (so `_elide_middle`'s `_coerced` runs), controls in
    # the head, the markup brackets in the surviving tail.
    hostile_id = "HLR-EVIL" + esc + rlo + zwsp + "x" * 40 + "[bold]x[/]"
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row(hostile_id, "review registry", "active"))
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "b")
        hint = _painted(screen, HintLine)
    assert esc not in hint, repr(hint)
    assert rlo not in hint, repr(hint)
    assert zwsp not in hint, repr(hint)
    assert "[bold]x[/]" in hint, hint  # markup brackets paint literally
    assert "\ufffd" in hint, hint  # the control bytes were coerced


# ---------------------------------------------------------------------------
# AT-097 — the review scope binds through the seat and home opens by `v`
# ---------------------------------------------------------------------------
async def test_at_097_review_scope_binds_through_the_seat_and_home_opens_by_v(tmp_path):
    _mixed(tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        bar = _painted(screen, KeyBar)
    # the review-scope glyphs are advertised; `b` is the arm affordance
    # (`mark reviewed`), and `↵` (enter) appears ONLY while armed (U3)
    for glyph, label in (("\u2191", "previous object"), ("\u2193", "next object"),
                         ("4", "cycle filter"), ("b", "mark reviewed")):
        assert f"{glyph} {label}" in bar, (glyph, label, bar)
    assert "\u21b5" not in bar, bar


# ---------------------------------------------------------------------------
# AT-099 — 2 000 objects scroll with the cursor in view and a constant
# render_line count per move
# ---------------------------------------------------------------------------


def _bulk_canon(count: int) -> str:
    return CANON_HEADER + "".join(_row(f"HLR-BULK.{i}", f"Statement {i}.", "active") for i in range(count))


async def test_at_099_two_thousand_objects_scroll_with_the_cursor_in_view(tmp_path):
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, _bulk_canon(2000))
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        listing = screen.query_one(ReviewList)
        # the counted-operations bound: a single cursor-move repaint renders a
        # constant window (the render_line calls), independent of N
        real = listing.render_line
        calls = {"n": 0}

        def counted(y):
            calls["n"] += 1
            return real(y)

        listing.render_line = counted
        await pilot.press("down")
        await pilot.pause()
        one_move = calls["n"]
        calls["n"] = 0
        await pilot.press("down")
        await pilot.pause()
        assert calls["n"] == one_move and one_move > 0, (one_move, calls["n"])
        listing.render_line = real

        await pilot.press(*(["down"] * 1997))
        await pilot.pause()
        frame = _frame(screen)
    # the selected row's marker is only ever painted by the LIST (the detail pane
    # also names the id, which would hide a list that never scrolled: M-RS20)
    assert "▸ HLR-BULK.1999" in frame, frame


async def test_at_099_render_line_count_constant_across_n(tmp_path):
    """The counted-operations bound: a single cursor-move repaint renders a
    constant window, independent of the object count (1 000 vs 2 000)."""
    small = tmp_path / "small"
    large = tmp_path / "large"
    for root, n in ((small, 1000), (large, 2000)):
        env = _init_repo(root)
        _set_identity(root, env, REVIEWER2)
        _seed_team(root, env)
        _write_canon(root, _bulk_canon(n))

    counts = {}
    for root in (small, large):
        app = MapperApp(root)
        async with app.run_test(size=(118, 34)) as pilot:
            await pilot.pause()
            screen = await _open_review(app, pilot)
            listing = screen.query_one(ReviewList)
            real = listing.render_line
            n_calls = {"n": 0}

            def counted(y):
                n_calls["n"] += 1
                return real(y)

            listing.render_line = counted
            await _press(pilot, "down")
            listing.render_line = real
        counts[root.name] = n_calls["n"]
    assert counts["small"] > 0, counts  # F6: the counter really counted
    assert counts["small"] == counts["large"], counts


# ---------------------------------------------------------------------------
# AT-100 — `escape`/`q` cancel the arm and leave only when not armed
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("width", WIDTHS)
async def test_at_100_escape_or_q_cancels_the_arm_and_leaves_only_when_not_armed(tmp_path, width):
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))
    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "b")
        assert screen._armed is not None  # noqa: SLF001
        await _press(pilot, "escape")
        assert screen._armed is None  # noqa: SLF001
        assert isinstance(app.screen, ReviewScreen)  # stayed
        await _press(pilot, "b")
        await _press(pilot, "q")
        assert screen._armed is None  # noqa: SLF001
        assert isinstance(app.screen, ReviewScreen)  # stayed
        await _press(pilot, "q")  # not armed: leaves
        assert isinstance(app.screen, HomeScreen)
    assert _review_files(tmp_path) == []


# ---------------------------------------------------------------------------
# AT-101 — signing in the preset moves the cursor to the next row
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("width", WIDTHS)
async def test_at_101_signing_moves_the_cursor_to_the_next_row(tmp_path, width):
    _seed_reviewer(tmp_path)
    canon = CANON_HEADER + (
        _row("HLR-RH.1", "review registry", "active")
        + _row("HLR-RH.2", "digests and baselines", "active")
        + _row("HLR-RH.4", "immutable store", "active")
    )
    _write_canon(tmp_path, canon)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "4")  # needs action
        await _press(pilot, "down")  # move to the middle row (HLR-RH.2)
        selected_before = screen._selected_row().obj.id  # noqa: SLF001
        assert selected_before == "HLR-RH.2", selected_before
        await _press(pilot, "b")
        await _press(pilot, "enter")
        for _ in range(3):
            await asyncio.wait_for(app.workers.wait_for_complete(), timeout=60)
            await pilot.pause()
        selected_after = screen._selected_row().obj.id  # noqa: SLF001
    # the signed object left the preset; the cursor is now on the next open row
    assert selected_after == "HLR-RH.4", selected_after


# ---------------------------------------------------------------------------
# AT-102 — an author-of-batch viewer pressing `b` sees the named refusal
# ---------------------------------------------------------------------------


async def test_at_102_b_refuses_when_the_viewer_authored_the_object_batch(tmp_path):
    _seed_reviewer(tmp_path, viewer=ANA, authors={"2026-10-11-reqharness-batch": ["ana"]})
    _write_canon(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "b")
        hint = _painted(screen, HintLine)
    assert "authored this object's batch" in hint, hint
    assert _review_files(tmp_path) == []


# ---------------------------------------------------------------------------
# AT-103 — the armed hint elides the middle and keeps the tail
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("width", WIDTHS)
async def test_at_103_armed_hint_elides_the_middle_and_keeps_the_tail(tmp_path, width):
    long_id = "HLR-" + "x" * 80
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row(long_id, "review registry", "active"))
    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "b")
        hint = _painted(screen, HintLine)
        frame = _frame(screen)
    assert "enter confirms, any other key cancels" in hint, hint
    assert "\u2026" in hint, hint
    assert long_id not in hint, hint
    # M-RS31: painted, not merely composed -- the tail is not clipped at 87
    assert "any other key cancels" in frame, frame


# ---------------------------------------------------------------------------
# AT-104 — the armed state and refusals use the darkside tokens
# ---------------------------------------------------------------------------


def test_at_104_armed_state_and_refusals_use_the_darkside_tokens(monkeypatch):
    row = _Row(
        obj=derive.CanonObject(id="HLR-RH.1", class_id="HLR", fields={}, line=1),
        state=derive.STATE_NOT_REVIEWED,
        informative=False,
        last="\u2014",
    )
    armed = _list_row_text(row, selected=True, armed=True)
    assert any(f"on {darkside.ACCENT}" in str(span.style) for span in armed.spans), armed.spans

    refusal = _hint_text("cannot sign: x is retired", darkside.ALERT)
    assert any(str(span.style) == darkside.ALERT for span in refusal.spans), refusal.spans

    with monkeypatch.context() as patch:
        patch.setattr(darkside, "ACCENT", "#123456")
        armed2 = _list_row_text(row, selected=True, armed=True)
    assert any("#123456" in str(span.style) for span in armed2.spans), armed2.spans


# ---------------------------------------------------------------------------
# AT-103 / AT-104 painted -- the real surfaces, not helper calls (M-RS31/M-RS32)
# ---------------------------------------------------------------------------


def _segments(screen):
    """Every painted (text, style) run of the composited frame."""
    return [
        (seg.text, seg.style)
        for strip in screen._compositor.render_strips()  # noqa: SLF001
        for seg in strip
    ]


def _hex(color) -> str | None:
    return color.get_truecolor().hex if color is not None else None


async def test_at_103_the_painted_armed_hint_elides_the_middle_of_a_long_object(tmp_path):
    """118-wide: the both-ends-survive property needs a wide elision budget —
    at 87 only 1 head + 1 tail cell fit, so this arm runs at 118 (declared in
    `01-requirements.md` §5.2); the 87 tail arm is
    `test_at_103_armed_hint_elides_the_middle_and_keeps_the_tail`."""
    long_id = "HLR-HEAD" + "x" * 70 + "TAIL"
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row(long_id, "review registry", "active"))
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "b")
        hint = _painted(screen, HintLine)
    # both ends of the object survive, the middle is what was cut, and the
    # fixed `enter confirms` tail is never cut
    assert "sign HLR-HEAD" in hint and "TAIL \u00b7 digest" in hint, hint
    assert "\u2026" in hint and long_id not in hint, hint
    assert "enter confirms, any other key cancels" in hint, hint


def test_at_103_elide_middle_keeps_both_ends_within_the_cell_budget():
    value = "HLR-HEAD" + "x" * 40 + "TAIL"
    out = _elide_middle(value, 20)
    assert out.startswith("HLR-HEAD") and out.endswith("TAIL"), out
    assert out.count("\u2026") == 1 and darkside.shown_cells(out) == 20, out
    assert _elide_middle("short", 20) == "short"


@pytest.mark.parametrize("width", WIDTHS)
async def test_at_104_the_painted_armed_hint_and_row_carry_the_accent_token(tmp_path, width):
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))
    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        cold = [s for t, s in _segments(screen) if "enter confirms" in t]
        await _press(pilot, "b")
        runs = _segments(screen)
    assert not cold
    hint = [s for t, s in runs if "enter confirms" in t]
    assert hint and all(_hex(s.color) == darkside.ACCENT for s in hint), hint
    row = [s for t, s in runs if "HLR-RH.1" in t and "\u25b8" in t]
    assert row and all(_hex(s.bgcolor) == darkside.ACCENT for s in row), row


@pytest.mark.parametrize("width", WIDTHS)
async def test_at_104_the_painted_refusal_carries_the_alert_token(tmp_path, width):
    _seed_reviewer(tmp_path, viewer=QA1)  # qa-1 holds no req-reviewer
    _write_canon(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))
    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "b")
        runs = _segments(screen)
    refusal = [s for t, s in runs if "does not hold the req-reviewer role" in t]
    assert refusal and all(_hex(s.color) == darkside.ALERT for s in refusal), refusal


# ---------------------------------------------------------------------------
# AT-105 — no painted literal outside the §6.6 table ∪ the prototype set
# ---------------------------------------------------------------------------


def test_at_105_screen_paints_no_string_outside_the_copy_table_or_prototype():
    """LLR-RS.1.3 (U4 / M-RS30): the §6.6 copy table is byte-exact and every
    string literal is English (no non-ASCII letter reaches a literal)."""
    import unicodedata

    import mapper.screens.review as review_mod

    assert review_mod._SIGN_ARMED_HEAD == "sign "
    assert review_mod._SIGN_ARMED_DIGEST == " \u00b7 digest "
    assert review_mod._SIGN_ARMED_HEADWORD == " \u00b7 head "
    assert review_mod._SIGN_ARMED_TAIL == " \u2014 enter confirms, any other key cancels"
    assert review_mod._REFUSE_CHAIN == "cannot sign: registry not verifiable ({status})"
    assert review_mod._REFUSE_VIEWER == "cannot sign: {viewer} is not a declared person"
    assert review_mod._REFUSE_AMBIGUOUS == "cannot sign: several people match your git identity \u2014 declare exactly one"
    assert review_mod._REFUSE_NO_ROLE == "cannot sign: {viewer} does not hold the {role} role at this head"
    assert review_mod._REFUSE_OBJECT == "cannot sign: unknown object {object}"
    assert review_mod._REFUSE_RETIRED == "cannot sign: {object} is retired"
    assert review_mod._REFUSE_CLASS == "cannot sign: {object}'s class is not declared"
    assert review_mod._REFUSE_AUTHOR == "cannot sign: {viewer} authored this object's batch"
    assert review_mod._REFUSE_MOVED == "cannot sign: something changed since b (object, content, head or role) \u2014 press b to re-arm"
    assert review_mod._REFUSE_DUP == "cannot sign: this content was already signed"
    assert review_mod._REFUSE_LIMIT == "cannot sign: the review-file limit is reached"
    assert review_mod._EMPTY_CANON == "no canon objects"
    assert review_mod._EMPTY_HISTORY == "no review event names this id"
    assert review_mod._KEYBAR_ARMED == "enter sign \u00b7 any other key cancel"

    source = Path(review_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    literals = _module_literals(tree)
    letters = sorted(
        {
            char
            for value in literals
            for char in value
            if ord(char) > 127 and unicodedata.category(char).startswith("L")
        }
    )
    assert letters == [], letters

    # M-RS30: the census.  A string the screen can paint that is in neither the
    # §6.6 table nor the approved-prototype list must fail HERE, so adding or
    # changing any literal is a deliberate edit of this set (and a re-check
    # against `01-requirements.md` §6.6) -- never a silent drive-by.
    added = sorted(literals - PAINTABLE_LITERALS)
    removed = sorted(PAINTABLE_LITERALS - literals)
    assert not added and not removed, (added, removed)


def _module_literals(tree: ast.AST) -> set[str]:
    """Every non-blank `str` constant in the module except docstrings."""
    docstrings = {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        and ast.get_docstring(node, clean=False) is not None
    }
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
        and node.value.strip()
    }


# The audited set: the 15 §6.6 strings (and their dynamic fragments), the
# approved-prototype words (status/filter/legend/band/detail), widget ids, style
# words, key names, CSS.  The undeclared-viewer and no-repo resting hints that the
# roles screen paints are DELIBERATELY absent (not in §6.6).
PAINTABLE_LITERALS = {
    '\n    #review-body { height: 1fr; }\n    #review-detail { width: 46; }\n    #review-band { height: ',
    '\n    ReviewList { width: 1fr; height: 100%; overflow-x: hidden; }\n    ',
    '      digest ',
    '   (bound head ',
    '   4 cycles: ',
    '  (',
    '  head ',
    '  registry ',
    '  registry not verifiable \u2014 every derived state is suspended',
    '  viewer ',
    '  \xb7 ',
    ' (',
    ' b ',
    ' chain ',
    ' digest matches / stale   ',
    ' filter ',
    ' holds ',
    ' holds no ',
    ' mark reviewed',
    ' mark reviewed \u2014 ',
    'object',
    'objects',
    ' of ',
    ' on ',
    ' role',
    ' role at head ',
    ' sign \u2014 refused with the reason when you lack the role',
    ' signed with no ',
    ' unentitled ',
    ' unentitled review',
    ' \xb7 ',
    ' \xb7 digest ',
    ' \xb7 h',
    ' \xb7 head ',
    ' \u2014 enter confirms, any other key cancels',
    ' \u2042',
    ' \u2042 ',
    ' \u2192 ',
    ' \u2192 reviewer role ',
    ' \u2713 verified',
    '#',
    '#review-band',
    '#review-detail',
    '#review-filter',
    '#review-legend',
    '#review-list',
    '#review-status',
    ')',
    '+',
    ':',
    '; }\n    ',
    'all',
    'b',
    'bold ',
    'cannot sign: registry not verifiable ({status})',
    'cannot sign: several people match your git identity \u2014 declare exactly one',
    'cannot sign: something changed since b (object, content, head or role) \u2014 press b to re-arm',
    'cannot sign: the review-file limit is reached',
    'cannot sign: this content was already signed',
    'cannot sign: unknown object {object}',
    'cannot sign: {object} is retired',
    "cannot sign: {object}'s class is not declared",
    "cannot sign: {viewer} authored this object's batch",
    'cannot sign: {viewer} does not hold the {role} role at this head',
    'cannot sign: {viewer} is not a declared person',
    '{role}',
    'derived states are suspended \u2014 the chain does not verify',
    'digest now ',
    'ellipsis',
    'enter',
    'enter sign \xb7 any other key cancel',
    'esc',
    'escape',
    'home',
    'informative mark   ',
    'model',
    'needs action',
    'next \u25b8 ',
    'no canon objects',
    'no repo',
    'no review event names this id',
    'not ready \xb7 no repo',
    'on ',
    'q',
    'refused',
    'registry not verifiable \u2014 b signs nothing',
    'release readiness',
    'release readiness \u2014 BLOCKED',
    'review',
    'review history',
    'review-band',
    'review-body',
    'review-detail',
    'review-filter',
    'review-legend',
    'review-list',
    'review-status',
    'sign',
    'sign ',
    'signed',
    'statement',
    'statement  ',
    'verdict ',
    'viewer {viewer} ({roles}) \u2014 b signs only what your role covers',
    '\u2014',
    '\u2026',
    '\u21b5',
    '\u25b8 ',
    '\u2713',
    '\u2713 matches',
    '\u2713/\u2717',
    '\u2717',
    '\u2717 stale \u2014 content changed',
}



# ---------------------------------------------------------------------------
# AT-106 — a second `enter` while the sign worker runs is inert
# ---------------------------------------------------------------------------


async def test_at_106_second_enter_while_the_sign_worker_runs_is_inert(tmp_path, monkeypatch):
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))
    real = signing.sign_review
    gate = threading.Event()

    started: list[int] = []

    def slow(*args, **kwargs):
        started.append(1)
        assert gate.wait(5)
        return real(*args, **kwargs)

    monkeypatch.setattr(signing, "sign_review", slow)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "b")
        await _press(pilot, "enter")
        await pilot.pause()
        assert screen._signing  # noqa: SLF001
        await _press(pilot, "enter")  # inert while signing
        await _press(pilot, "b")  # also inert: nothing re-arms mid-sign
        assert screen._signing  # noqa: SLF001
        assert screen._armed is None  # noqa: SLF001
        gate.set()
        await asyncio.wait_for(app.workers.wait_for_complete(), timeout=60)
        await pilot.pause()
    assert len(started) == 1, started  # M-RS28: ONE sign worker, not two
    assert len(_review_files(tmp_path)) == 1


# ---------------------------------------------------------------------------
# AT-107 — the worker runs all disk/git work off the UI thread
# ---------------------------------------------------------------------------


async def test_at_107_worker_runs_all_disk_and_git_work_off_thread(tmp_path, monkeypatch):
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))

    gate = _Gate(identity_module._run_git, closed=False)
    monkeypatch.setattr(identity_module, "_run_git", gate)

    threads: dict[str, list[str]] = {}

    def record(label, fn):
        def wrapper(*args, **kwargs):
            threads.setdefault(label, []).append(threading.current_thread().name)
            return fn(*args, **kwargs)

        return wrapper

    # Patched where the screen looks them up (module attributes), so a call the
    # screen makes on the UI thread would land on the main thread's name.
    monkeypatch.setattr(release_mod, "safe_verify", record("verify_chain", release_mod.safe_verify))
    monkeypatch.setattr(derive, "load_canon", record("load_canon", derive.load_canon))
    monkeypatch.setattr(derive, "derive_states", record("derive_states", derive.derive_states))
    monkeypatch.setattr(release_mod, "evaluate", record("evaluate", release_mod.evaluate))
    monkeypatch.setattr(signing, "sign_review", record("sign_review", signing.sign_review))

    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await _press(pilot, "v")
        await _settle(app, pilot)
        screen = app.screen
        assert isinstance(screen, ReviewScreen)
        assert "HLR-RH.1" in _frame(screen)
        await _press(pilot, "b")
        await _press(pilot, "enter")
        await _settle(app, pilot)

    main = threading.main_thread().name
    for label in ("verify_chain", "load_canon", "derive_states", "evaluate", "sign_review"):
        assert threads.get(label), f"{label} was never recorded"
        assert all(t != main for t in threads[label]), (label, threads[label])
    assert gate.calls, "no git call recorded"
    assert all(not on_main for _tail, on_main in gate.calls), gate.calls
    assert len(_review_files(tmp_path)) == 1


# ---------------------------------------------------------------------------
# M-RS13 — a late SUCCESS on a popped screen paints nothing and raises nothing
# ---------------------------------------------------------------------------


async def test_at_107_late_snapshot_on_a_popped_screen_is_dropped(tmp_path, monkeypatch):
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))
    release_gate = threading.Event()
    real = derive.load_canon

    def slow(*args, **kwargs):
        assert release_gate.wait(30)
        return real(*args, **kwargs)

    monkeypatch.setattr(derive, "load_canon", slow)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await _press(pilot, "v")
        screen = app.screen
        assert isinstance(screen, ReviewScreen)
        await _press(pilot, "escape")  # the snapshot is still in flight
        assert isinstance(app.screen, HomeScreen)
        release_gate.set()
        await asyncio.wait_for(app.workers.wait_for_complete(), timeout=60)
        await pilot.pause()
        assert not screen._loaded  # noqa: SLF001 — nothing was applied
        # Textual cancels a dead screen's workers, so the framework alone never
        # delivers the late result: hand the dead screen a SUCCESS for its own
        # generation and its hand-back guard must drop it (no paint, no raise).
        late = SimpleNamespace(
            state=WorkerState.SUCCESS,
            worker=SimpleNamespace(
                result=(screen._gen, _load(*_discover(tmp_path)))  # noqa: SLF001
            ),
        )
        screen.on_worker_state_changed(late)
        assert not screen._loaded  # noqa: SLF001
        assert isinstance(app.screen, HomeScreen)


# ---------------------------------------------------------------------------
# M-RS33 — an armed `down` cancels: `b`, `down`, `enter` writes nothing
# ---------------------------------------------------------------------------


async def test_at_093_b_down_enter_writes_nothing(tmp_path):
    _seed_reviewer(tmp_path)
    _write_canon(
        tmp_path,
        CANON_HEADER
        + _row("HLR-RH.1", "review registry", "active")
        + _row("HLR-RH.2", "digests and baselines", "active"),
    )
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "b")
        assert screen._armed is not None  # noqa: SLF001
        await _press(pilot, "down")
        assert screen._armed is None  # noqa: SLF001
        await _press(pilot, "enter")
        await app.workers.wait_for_complete()
        await pilot.pause()
    assert _review_files(tmp_path) == []


# AT-093 (copy promise) — ANY other key cancels the arm, bound or not
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("key", ["x", "5", "space", "b"])
async def test_at_093_any_other_key_cancels_the_arm_and_a_later_enter_writes_nothing(tmp_path, key):
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "b")
        assert screen._armed is not None  # noqa: SLF001
        await _press(pilot, key)
        assert screen._armed is None, key  # noqa: SLF001
        assert isinstance(app.screen, ReviewScreen)
        await _press(pilot, "enter")
        await app.workers.wait_for_complete()
        await pilot.pause()
    assert _review_files(tmp_path) == []


# ---------------------------------------------------------------------------
# RS2 review follow-up (code/security F1–F3, UX U1–U5 + notices)
# ---------------------------------------------------------------------------


async def test_f1_sign_result_survives_a_resume_and_clears_signing(tmp_path, monkeypatch):
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))
    real = signing.sign_review
    gate = threading.Event()

    def slow(*args, **kwargs):
        assert gate.wait(10)
        return real(*args, **kwargs)

    monkeypatch.setattr(signing, "sign_review", slow)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "b")
        await _press(pilot, "enter")
        await pilot.pause()
        assert screen._signing  # noqa: SLF001
        await _press(pilot, "ctrl+p")  # suspend (palette) …
        await _press(pilot, "escape")  # … and resume: bumps the load generation
        await pilot.pause()
        gate.set()
        await asyncio.wait_for(app.workers.wait_for_complete(), timeout=60)
        await pilot.pause()
        assert not screen._signing  # noqa: SLF001 — a sign result always clears
    assert len(_review_files(tmp_path)) == 1


async def test_f2_sign_worker_write_failure_refuses_and_stays_alive(tmp_path, monkeypatch):
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))

    def boom(*_a, **_k):
        raise PermissionError("denied")

    monkeypatch.setattr(signing, "record_review", boom)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "b")
        await _press(pilot, "enter")
        await asyncio.wait_for(app.workers.wait_for_complete(), timeout=60)
        await pilot.pause()
        hint = _painted(screen, HintLine)
        assert not screen._signing  # noqa: SLF001
        assert isinstance(app.screen, ReviewScreen)  # the app stayed alive
    assert "cannot sign: registry not verifiable (chain broken)" in hint, hint
    assert _review_files(tmp_path) == []


async def test_f2_load_worker_failure_refuses_and_stays_alive(tmp_path, monkeypatch):
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))

    def boom(*_a, **_k):
        raise PermissionError("denied")

    monkeypatch.setattr(reviews, "load_reviews", boom)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        await _press(pilot, "v")
        screen = app.screen
        assert isinstance(screen, ReviewScreen)
        # `wait_for_complete` re-raises WorkerFailed on the failed worker, so
        # poll for the ERROR refusal instead (exit_on_error=False keeps it alive).
        await _until(lambda: "cannot sign" in _painted(screen, HintLine), "the ERROR refusal")
        hint = _painted(screen, HintLine)
        assert not screen._signing  # noqa: SLF001
        assert isinstance(app.screen, ReviewScreen)  # the app stayed alive
    assert "cannot sign: registry not verifiable (chain broken)" in hint, hint


async def test_f3_applying_a_snapshot_cancels_the_arm(tmp_path):
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "b")
        assert screen._armed is not None  # noqa: SLF001
        await app.push_screen(Screen())
        await pilot.pause()
        app.pop_screen()
        await pilot.pause()
        await asyncio.wait_for(app.workers.wait_for_complete(), timeout=60)
        await pilot.pause()
        assert screen._armed is None  # noqa: SLF001 — re-discovery cancels the arm
    assert _review_files(tmp_path) == []


@pytest.mark.parametrize("width", WIDTHS)
async def test_u1_long_object_id_truncates_with_ellipsis_in_the_list(tmp_path, width):
    long_id = "HLR-" + "x" * 80
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row(long_id, "review registry", "active"))
    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "b")
        hint = _painted(screen, HintLine)
        frame = _frame(screen)
    assert long_id not in frame, frame  # the id never paints in full
    assert "\u25b8 HLR-" in frame, frame  # the selected row keeps the prefix
    assert "\u2026" in frame, frame
    assert "enter confirms, any other key cancels" in hint, hint


async def test_u2_list_cells_are_bounded_by_the_column_width(tmp_path):
    _mixed(tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(87, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        listing = screen.query_one(ReviewList)
        width = listing.size.width
        frame = _frame(screen)
    assert "digest now" in frame, frame  # the detail pane still paints
    for text in listing._rows:  # noqa: SLF001
        assert text.cell_len <= max(0, width - 1), (text.cell_len, width)


async def test_u3_armed_key_bar_shows_only_the_armed_text(tmp_path):
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "b")
        bar = _painted(screen, KeyBar)
    assert "enter sign \u00b7 any other key cancel" in bar, bar
    assert "mark reviewed" not in bar, bar


async def test_u3_read_only_key_bar_hides_b_and_enter(tmp_path):
    _mixed(tmp_path)
    from tests.test_roles_screen import _read_docs, _write_docs

    docs = _read_docs(tmp_path)
    docs[2]["role"] = "admin"
    _write_docs(tmp_path, docs)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        bar = _painted(screen, KeyBar)
    assert "mark reviewed" not in bar, bar
    assert "\u21b5" not in bar, bar
    assert "previous object" in bar, bar  # navigation is still advertised


async def test_u3_loading_key_bar_advertises_only_escape(tmp_path, monkeypatch):
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))
    gate = threading.Event()
    real = derive.load_canon

    def slow(*args, **kwargs):
        assert gate.wait(10)
        return real(*args, **kwargs)

    monkeypatch.setattr(derive, "load_canon", slow)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        await _press(pilot, "v")
        await pilot.pause()
        screen = app.screen
        bar = _painted(screen, KeyBar)
        gate.set()
        await asyncio.wait_for(app.workers.wait_for_complete(), timeout=60)
        await pilot.pause()
    assert "esc back" in bar, bar
    assert "mark reviewed" not in bar, bar
    assert "previous object" not in bar, bar


async def test_u4_loading_band_shows_the_prototype_heading(tmp_path, monkeypatch):
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))
    gate = threading.Event()
    real = derive.load_canon

    def slow(*args, **kwargs):
        assert gate.wait(10)
        return real(*args, **kwargs)

    monkeypatch.setattr(derive, "load_canon", slow)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        await _press(pilot, "v")
        await pilot.pause()
        screen = app.screen
        band = _render_text(screen, "review-band", 118)
        gate.set()
        await asyncio.wait_for(app.workers.wait_for_complete(), timeout=60)
        await pilot.pause()
    assert "release readiness" in band, band
    assert "verdict" not in band, band  # no verdict line while loading


async def test_u5_short_object_id_stays_intact_at_87(tmp_path):
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))
    app = MapperApp(tmp_path)
    async with app.run_test(size=(87, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "b")
        hint = _painted(screen, HintLine)
    assert "sign HLR-RH.1 \u00b7 digest" in hint, hint  # the object is intact
    assert "\u2026" not in hint, hint
    assert "enter confirms, any other key cancels" in hint, hint


async def test_notice_legend_stays_on_one_row_at_87(tmp_path):
    _mixed(tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(87, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        legend = _render_text(screen, "review-legend", 87)
    assert "\n" not in legend, legend
    assert "informative mark" in legend, legend


async def test_notice_registry_counts_singular_object(tmp_path):
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER + _row("HLR-RH.1", "review registry", "active"))
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        status = _plain(screen, "review-status")
    assert "registry 1 object" in status, status
    assert "registry 1 objects" not in status, status


async def test_notice_b_on_empty_canon_is_inert(tmp_path):
    _seed_reviewer(tmp_path)
    _write_canon(tmp_path, CANON_HEADER)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = await _open_review(app, pilot)
        await _press(pilot, "b")
        hint = _painted(screen, HintLine)
        assert screen._armed is None  # noqa: SLF001
    assert "cannot sign" not in hint, hint  # no refusal with a missing name
    assert _review_files(tmp_path) == []


def test_n2_a_stale_worker_error_does_not_clear_an_in_flight_sign():
    """RS2 review N2: a load worker that fails while a sign is in flight must
    not clear `_signing` (which would re-enable `b` mid-sign); only the sign
    worker's own failure clears it, and a stale worker is ignored."""
    from types import SimpleNamespace

    from textual.worker import WorkerState

    from mapper.screens.review import ReviewScreen

    calls: list[str] = []
    sign_job, load_job, stale_job = object(), object(), object()
    fake = SimpleNamespace(
        _sign_job=sign_job,
        _load_job=load_job,
        _signing=True,
        _handle_worker_error=lambda: calls.append("handled"),
    )

    for worker in (load_job, stale_job):
        ReviewScreen.on_worker_state_changed(
            fake, SimpleNamespace(state=WorkerState.ERROR, worker=worker)
        )
    assert calls == [], "a load/stale worker failure touched an in-flight sign"

    ReviewScreen.on_worker_state_changed(
        fake, SimpleNamespace(state=WorkerState.ERROR, worker=sign_job)
    )
    assert calls == ["handled"]
