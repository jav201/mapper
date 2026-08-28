"""Tests for mapper.app."""
import pytest
from textual.widgets import Static

from mapper.app import HomeScreen, MapScreen, MapperApp, NavigationModel, PlugRepoScreen, RepoScreen
from mapper.model import Edge, Ficha, Graph, Node
from mapper.views.state import ViewState


async def test_plug_repo_url_flow(tmp_path, monkeypatch):
    from mapper.app import PlugRepoScreen
    from mapper.screens import HelpScreen

    fake_graph = Graph()
    fake_graph.add_node(Node(id="jav201/s19_app", ficha=Ficha(title="s19_app")))

    def fake_fetch(self, progress=None):
        if progress:
            progress(1, 1, "listo")
        return fake_graph

    monkeypatch.setattr("mapper.app.GitHubConnector.fetch", fake_fetch)

    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        app.push_screen(PlugRepoScreen())
        await pilot.pause()
        input_widget = app.screen.query_one("#repo-input")
        input_widget.value = "https://github.com/jav201/s19_app"
        await pilot.press("enter")
        await pilot.pause()
        # Should now be on RepoScreen with the normalized slug.
        assert isinstance(app.screen, RepoScreen)
        assert app.screen.repo == "jav201/s19_app"


def test_plug_repo_normalizes_github_url():
    assert PlugRepoScreen._normalize_repo("jav201/s19_app") == "jav201/s19_app"
    assert (
        PlugRepoScreen._normalize_repo("https://github.com/jav201/s19_app")
        == "jav201/s19_app"
    )
    assert (
        PlugRepoScreen._normalize_repo("https://github.com/jav201/s19_app.git")
        == "jav201/s19_app"
    )
    assert PlugRepoScreen._normalize_repo("git@github.com:jav201/s19_app.git") == "jav201/s19_app"


def test_navigation_model():
    g = Graph()
    g.add_node(Node(id="a"))
    g.add_node(Node(id="b"))
    g.add_node(Node(id="c"))
    g.add_edge(Edge("a", "b"))
    g.add_edge(Edge("a", "c"))
    nav = NavigationModel(g)
    assert nav.cursor == "a"
    nav.cursor = "b"
    assert nav.next_sibling() == "c"
    assert nav.prev_sibling() is None
    assert nav.parent() == "a"


def test_map_screen_renders():
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="Root")))
    g.add_node(Node(id="child", ficha=Ficha(title="Child")))
    g.add_edge(Edge("root", "child"))
    screen = MapScreen("test")
    screen.graph = g
    screen.nav = NavigationModel(g)
    # Just ensure render does not blow up
    text = screen.renderer.render(g, ViewState(selected_id="root", w=60, h=20))
    assert "Root" in text.plain


async def test_repo_screen_two_pane_renders(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        app.push_screen(RepoScreen("jav201/taskboard"))
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, RepoScreen)
        # After mounting the table widget should exist.
        table = screen.query_one("#repo-table", Static)
        assert table is not None


async def test_focus_active_blocks_structural_edits(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        # Seed a map with two children.
        store = app.store
        g = Graph()
        g.add_node(Node(id="root", ficha=Ficha(title="Root")))
        g.add_node(Node(id="keep", ficha=Ficha(title="Keep")))
        g.add_node(Node(id="focus-root", ficha=Ficha(title="Focus Root")))
        g.add_edge(Edge("root", "keep"))
        g.add_edge(Edge("root", "focus-root"))
        store.save("focus-test", g)

        app.push_screen(MapScreen("focus-test"))
        await pilot.pause()
        screen = app.screen
        screen.nav.cursor = "focus-root"
        screen.action_toggle_focus()
        await pilot.pause()
        assert screen.focus_active

        # Attempt to add a child while focused: should be blocked.
        screen.action_add_child()
        await pilot.pause()
        # Map on disk must still contain all original nodes.
        loaded = store.load("focus-test")
        assert set(loaded.nodes) == {"root", "keep", "focus-root"}


async def test_llr_cnv_3_1_focus_owner_tracks_the_real_focus(tmp_path):
    """The screen supplies the owner from the app's ACTUAL focused widget.

    Driven with the REAL `tab` key, never `.focus()`.  The prototypes that
    approved this batch were SVG renders from Python generators -- nothing ran
    Textual -- so every interaction in them is unverified for the target
    framework, and a proxy that bypasses the real mechanism would verify the
    proxy.  A previous batch shipped a keyboard gap exactly that way.

    THE TERMINAL SIZE IS PART OF THE TEST, and getting it wrong manufactured a
    defect that does not exist.  `run_test()` defaults to 80x24, where
    `_apply_region_visibility` auto-hides BOTH the rail and the inspector --
    correctly, for a narrow terminal -- leaving `focus_chain` empty and nothing
    for `tab` to reach.  Measured:

        80 x 24   chain=[]                          owners=['', '', '', '', '']
        118 x 34  chain=['map-rail','insp-title',   owners=['', 'rail', 'inspector',
                         'insp-state','insp-notes']         'inspector','inspector']
        140 x 45  same as 118 x 34

    Index 0 is `''` once `_park_focus` has landed.  Sampled a single
    `pilot.pause()` after `push_screen` it is still AUTO_FOCUS's transient
    `'rail'` -- 23 runs in 25 -- which is why this arm settles twice and
    asserts the pre-state before measuring anything.

    So this runs at **118 x 34, the batch's declared context of use**, and
    asserts `LLR-CNV.3.1`'s real threshold, which DOES reproduce there.  An
    earlier revision of this file recorded the 80x24 reading as a shipped
    "tab drops focus" defect and carried it; that was wrong, and the retraction
    is `A-96`.  This is the batch's own `P-20` lesson inverted: a suite that
    runs at one size sees only what that size shows.
    """
    from mapper.views.state import FOCUS_OWNERS

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        g = Graph()
        g.add_node(Node(id="root", ficha=Ficha(title="Raiz")))
        g.add_node(Node(id="hijo", ficha=Ficha(title="Hijo")))
        g.add_edge(Edge("root", "hijo"))
        app.store.save("focus-owner", g)

        app.push_screen(MapScreen("focus-owner"))
        await pilot.pause()
        # A SECOND settle, and it is load-bearing.  `on_mount` schedules
        # `call_after_refresh(self._park_focus)`, which sets focus to None,
        # while Textual's AUTO_FOCUS has already focused `#map-rail`.  Sampled
        # one pause in, the screen is usually still in the AUTO_FOCUS state
        # (measured 23 of 25 runs), so the pre-state below would be a transient
        # and the first assertion would hold only because `_park_focus` happens
        # to land between the sample and the first key press.
        await pilot.pause()
        screen = app.screen
        assert app.focused is None, (
            "the pre-state must be settled, not AUTO_FOCUS's transient"
        )

        seen = [screen._focus_owner()]
        # `LLR-CNV.3.1`'s pre-state is "from the canvas".  `#map-canvas` is
        # `can_focus=False` (`B-53`), so nothing-focused is the reachable
        # equivalent: both give owner "" and both enter Textual's `_move_focus`
        # at chain index 0.  Stated, because an unstated substitution is exactly
        # what `A-96` is about.
        assert seen[0] == "", f"unsettled pre-state: {seen[0]!r}"
        for _ in range(4):
            # Every sample is also checked against a recomputation from
            # `app.focused`, so the derivation is asserted at each step and not
            # only at the endpoints.
            assert seen[-1] in FOCUS_OWNERS, seen
            assert seen[-1] == _expected_owner(app, screen)
            assert screen._view_state(80, 24).focus_owner == seen[-1]
            await pilot.press("tab")
            await pilot.pause()
            seen.append(screen._focus_owner())

        # `LLR-CNV.3.1`'s DECLARED THRESHOLD, driven with the real key.
        # `M-10`'s recorded pre-state: press 1 focuses the rail, press 2 the
        # inspector's first field.
        assert seen[1] == "rail", f"after one tab: {seen}"
        assert seen[2] == "inspector", f"after two tabs: {seen}"

        # TWO EARLIER REVISIONS OF THIS ARM WERE WRONG, both recorded because
        # the second is the more instructive:
        #   1. `len(set(seen)) > 1` -- "the owner changed" -- passed at 80x24
        #      via the degenerate transition rail -> nothing focused.
        #   2. The repair carried that 80x24 reading forward as a real defect
        #      and asserted the screen has no focus chain. It has one, at any
        #      size where the regions are actually displayed.


async def test_llr_cnv_3_1_the_parent_walk_maps_a_nested_widget_to_its_region(tmp_path):
    """The PARENT WALK, which nothing else executes.

    `_focus_owner` climbs from the focused widget to a declared region, and the
    arm above only ever observes `'rail'` and `''` -- both of which resolve on
    the first iteration, so the loop's actual job is never exercised.  Measured:
    mutating `_focus_owner` to stop walking parents left that arm GREEN.

    `#insp-title` is a CHILD of `#map-inspector`, so this is the reachable state
    that makes the climb load-bearing.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        g = Graph()
        g.add_node(Node(id="root", ficha=Ficha(title="Raiz")))
        app.store.save("walk", g)
        app.push_screen(MapScreen("walk"))
        await pilot.pause()
        screen = app.screen

        title = screen.query_one("#insp-title")
        assert title.id != "map-inspector", "the probe needs a nested widget, not the region itself"
        title.focus()
        await pilot.pause()
        assert screen._focus_owner() == "inspector"


def _expected_owner(app, screen) -> str:
    """The owner, recomputed from `app.focused` -- a TRANSCRIPTION, not an
    independent oracle.

    It re-implements the same parent walk over the same roster, so a defect in
    the walk is reproduced by the check.  Measured: it catches "ignores
    `app.focused`" and "not wired through", and does NOT catch "stops walking
    parents".  That last case is covered by the arm above instead.
    """
    node = app.focused
    while node is not None:
        for region_id, owner in type(screen)._FOCUS_REGIONS:
            if getattr(node, "id", None) == region_id:
                return owner
        node = getattr(node, "parent", None)
    return ""


async def test_the_focus_chain_is_a_function_of_terminal_size(tmp_path):
    """The measurement that RETRACTED a defect this batch had already recorded.

    `MapScreen`'s focus chain is empty at 80x24 and populated at the declared
    context of use.  That is `_apply_region_visibility` working: below
    `MIN_CANVAS_WIDTH` it auto-hides the rail and the inspector so the canvas
    keeps the terminal, and a hidden widget is correctly not in the chain.

    An earlier revision measured only the default `run_test()` size, read the
    empty chain as "tab drops focus on MapScreen", wrote it into requirement
    amendment `A-94`, carried it as `B-51`, and pinned it as a strict xfail.
    All of that was wrong -- retracted by `A-96`.

    This arm exists so the next person meets the explanation instead of
    rediscovering the phantom.  It is also the positive control the absence
    needed: the same probe returns a NON-empty chain, so "empty at 80x24" is a
    measurement rather than a probe that cannot see anything.
    """
    async def chain_at(size):
        app = MapperApp(tmp_path)
        async with app.run_test(size=size) as pilot:
            await pilot.pause()
            g = Graph()
            g.add_node(Node(id="root", ficha=Ficha(title="Raiz")))
            app.store.save("sized", g)
            app.push_screen(MapScreen("sized"))
            await pilot.pause()
            return [getattr(w, "id", None) for w in app.screen.focus_chain]

    narrow = await chain_at((80, 24))
    declared = await chain_at((118, 34))

    assert narrow == [], f"the rail and inspector should be auto-hidden at 80x24: {narrow}"
    assert declared, "the declared context of use must have something to traverse"
    assert "map-rail" in declared and any(w and w.startswith("insp-") for w in declared), (
        f"the chain should reach both the rail and the inspector: {declared}"
    )


def _tone_at(text, needle: str) -> str:
    start = text.plain.index(needle)
    return " ".join(str(s.style) for s in text.spans if s.start <= start < s.end)


async def test_an_export_never_encodes_where_the_keyboard_was(tmp_path, monkeypatch):
    """An exported SVG is a STANDALONE artifact.

    `_view_state()` carries the live focus owner, which is right for the canvas
    and wrong for a file that leaves the screen -- "which region owns the
    keyboard" has no meaning inside it.  Measured before this arm existed: the
    rail holds focus on mount, so a ROUTINE export painted the selected node in
    the INACTIVE tone.

    Nothing caught it.  The byte-identity digests call renderers directly with a
    default state, and the AT-009 export tests build their own `ViewState`
    rather than going through the screen -- so the one path that carries a live
    owner was the one path no test drove.  This drives the SHIPPED export action
    and captures what it actually handed the writer.
    """
    from mapper.views.layered import LayeredRenderer
    from mapper.views.state import ViewState

    captured = {}
    monkeypatch.setattr("mapper.app.save_svg",
                        lambda text, path: captured.update(text=text, path=path))

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        g = Graph()
        g.add_node(Node(id="root", ficha=Ficha(title="Raiz")))
        g.add_node(Node(id="hijo", ficha=Ficha(title="Hijo")))
        g.add_edge(Edge("root", "hijo"))
        app.store.save("exportfocus", g)
        app.push_screen(MapScreen("exportfocus"))
        await pilot.pause()
        screen = app.screen
        screen.nav.cursor = "root"

        # Focus here is a PRECONDITION, not the mechanism under test, so it is
        # established directly rather than raced for.  The mechanism this arm
        # covers is the export's state construction; C-16's ban on proxies is
        # about not bypassing the mechanism a requirement is ABOUT, and waiting
        # on real focus made this test flaky for a reason unrelated to exports
        # (measured: `app.focused` still None after 5s under load -- carry
        # `B-51`).
        screen.query_one("#map-rail").focus()

        # THE PRECONDITION IS WAITED FOR, ON A BOUND, not assumed to land in one
        # pump.  `focus()` posts a message; one `pilot.pause()` is one turn of
        # the pump and is usually -- not always -- enough.  Measured on this
        # tree, the positive control below failed 1 run in 11 with
        # `_focus_owner()` still `""`, which is a verdict about scheduling and
        # not about exports.  Waiting is not the same as assuming: the loop
        # fails LOUDLY and names what never happened, so a focus mechanism that
        # genuinely broke still reddens this arm instead of hanging or passing.
        #
        # It also doubles as the positive control it replaces: the live owner is
        # genuinely non-default before the export runs, so the assertion at the
        # end discriminates rather than being accidentally true.
        for _ in range(50):
            if screen._focus_owner() not in ("", "canvas"):
                break
            await pilot.pause()
        else:
            raise AssertionError(
                f"focus never left {screen._focus_owner()!r} in 50 pumps after "
                f"`#map-rail`.focus(); the precondition this arm needs was never "
                f"established, so it could not tell the two focus states apart"
            )

        # The REAL key, not the action method.  Export is promised as a
        # keystroke -- `keymap.py` binds `e` -> `export_svg` in the `view`
        # group -- so calling the action directly would skip the binding this
        # arm's docstring claims to drive, and could not see it broken.
        await pilot.press("e")
        await pilot.pause()

    assert "text" in captured, "the real 'e' key never reached the export writer"
    exported_tone = _tone_at(captured["text"], "Raiz")

    focused = LayeredRenderer().render(g, ViewState(selected_id="root", w=80, h=24))
    inactive = LayeredRenderer().render(
        g, ViewState(selected_id="root", w=80, h=24, focus_owner="inspector"))
    assert _tone_at(focused, "Raiz") != _tone_at(inactive, "Raiz"), (
        "the two tones are identical, so this arm proves nothing"
    )
    assert exported_tone == _tone_at(focused, "Raiz")


async def test_b50_the_export_carries_the_diff_the_canvas_is_showing(tmp_path, monkeypatch):
    """The increment's ONE declared behaviour change, actually covered.

    Before the parameter object, this site passed `query` and omitted `diff`, so
    an SVG exported during a diff silently lost its tinting -- the measured
    defect that decided the renderer contract.  §6 claimed the fix was
    "covered"; it was not.  Executed on the full suite with `diff=None` forced
    back into `_view_state`: `716 passed` -- green, because no test anywhere
    passed `diff=` or `query=`.  A claim of coverage that the suite contradicts
    is worse than an acknowledged gap.
    """
    captured = {}
    monkeypatch.setattr("mapper.app.save_svg",
                        lambda text, path: captured.update(text=text))

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        g = Graph()
        g.add_node(Node(id="root", ficha=Ficha(title="Raiz")))
        g.add_node(Node(id="hijo", ficha=Ficha(title="Hijo")))
        g.add_edge(Edge("root", "hijo"))
        app.store.save("exportdiff", g)
        app.push_screen(MapScreen("exportdiff"))
        await pilot.pause()
        screen = app.screen
        screen.nav.cursor = "root"

        # Capture the state the shipped export hands the renderer.
        seen = {}
        real = screen._current_renderer

        def spy():
            renderer = real()

            class Spy:
                def render(self, graph, state):
                    seen["state"] = state
                    return renderer.render(graph, state)

            return Spy()

        monkeypatch.setattr(screen, "_current_renderer", spy)

        screen.query_text = "hij"
        screen.diff_active = True
        screen.diff = object()          # a sentinel: only its presence matters here
        # The REAL key, matching this file's sibling export arm.  `keymap.py`
        # binds `e` -> `export_svg` in the `view` group, so a direct
        # `action_export_svg()` call cannot see that binding broken -- and
        # C-16's gloss names a direct `action_*` call alongside `.focus()`.
        await pilot.press("e")
        await pilot.pause()

    assert "state" in seen, "the real 'e' key never reached the renderer"
    assert seen["state"].diff is screen.diff, (
        "the export dropped the active diff -- the exact under-fill the parameter "
        "object exists to prevent"
    )
    assert seen["state"].query == "hij", "the export dropped the active query"
    assert seen["state"].focus_owner == "", "the export must not carry live focus"


async def test_home_screen_renders_hero_when_maps_exist(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        store = app.store
        g = Graph()
        g.add_node(Node(id="root", ficha=Ficha(title="Root")))
        g.add_node(Node(id="a", ficha=Ficha(title="A")))
        g.add_edge(Edge("root", "a"))
        store.save("hero-test", g)
        store.record_session("hero-test", "root")

        app.push_screen(HomeScreen())
        await pilot.pause()
        screen = app.screen
        hero = screen.query_one("#home-hero", Static)
        assert hero is not None
        assert "nodos sin acta" in hero.render().plain


async def test_settings_screen_canary_mounts(tmp_path):
    from mapper.screens.settings import SettingsScreen

    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        app.push_screen(SettingsScreen())
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, SettingsScreen)
        grid = screen.query_one("#settings-grid")
        assert grid is not None
