"""Inc-REPAIR S-E — the sidecar's shipped defects, and the coercion sink beside them.

`AT-049` (`B-29`, `LLR-REPAIR.1`) · `AT-050` (`B-30`, `LLR-REPAIR.2`) ·
`B-48` (the attachments phantom) · `LLR-N13.1.7` (alias amplification) ·
the `screens/coverage.py` coercion sink.

**`AT-049` AND `AT-050` HAD NO NODES ON DISK.** They were ratified in
`01-requirements.md` §3.9 and never written — the `AT-005`/`AT-006` shape this
batch already carries, found at the pre-gate before any fix.

**AND THIS MODULE IS NOT ALL OF `AT-049`.** It is `AT-050`'s whole home and only
the STORE half of `AT-049`. §3.9's boundary catalog asks the positive arm for
*"the card enters the damaged state"* and the negative arm for *"no warning **and
a healthy card**"*; neither card assertion is here, and neither can be written
here, because there is no damaged card state in the code — `HomeScreen` reports a
damaged load as a TOAST (`app.py:546-551`, `app.py:1277-1290`) and the recents
table has no damaged column or style.

That is a hand-off, not an omission. §5.4 says `LLR-REPAIR.1` gates `Inc-7`
*"because without it `AT-025b` is vacuous"*, and `LLR-N13.1.5` identifies the
damaged maps *"by the load path raising or **recording a load warning**, never by
a clock"* — so the warning these arms pin is precisely what the card will be
painted from. `AT-025b` has no node on disk either; the card clause and the
containment arm that consumes it land together at `Inc-7`.

So: do not read a green run of this module as `AT-049` discharged.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from mapper.store import MapStore, MapStoreError

MMD = "graph TD\n    raiz[Raiz]\n    raiz --> hijo[Hijo]\n"


def _write(tmp_path, sidecar: str):
    (tmp_path / "m.mmd").write_text(MMD, encoding="utf-8")
    (tmp_path / "m_nodos.yml").write_text(sidecar, encoding="utf-8")
    return MapStore(tmp_path)


def amplified(levels: int, fanout: int = 10) -> str:
    """A sidecar whose two `documents` share an alias-amplified `name`.

    TWO documents, because the defect lives in the DUPLICATE branch -- a single
    amplified name never reaches the line that interpolates it.
    """
    lines = ["_anchors:", "  a: &l0 x"]
    for i in range(1, levels + 1):
        refs = ", ".join([f"*l{i-1}"] * fanout)
        lines.append(f"  n{i}: &l{i} [{refs}]")
    deep = f"*l{levels}"
    return "\n".join(lines) + "\n" + "\n".join([
        "schema: []",
        "documents:",
        f"  - name: {deep}",
        "    path: a.pdf",
        f"  - name: {deep}",
        "    path: b.pdf",
        "nodes:",
        "  raiz:",
        "    title: benigno",
        "",
    ])


# ---------------------------------------------------------------------------
# AT-049 / LLR-REPAIR.1 / B-29


def test_at049_a_phantom_sidecar_id_records_a_load_warning(tmp_path):
    """A sidecar id the `.mmd` never defines must be NAMED in a load warning.

    `LLR-REPAIR.1`'s threshold is quantified over EVERY phantom id, not over the
    fixture's one, so two are planted and both must be named.

    Measured pre-fix: `load_warnings == []`. Nothing named either. That silence
    matters beyond tidiness -- `LLR-N13.1.5`'s containment arm, which `AT-025b`
    drives and `HLR-N13.3` leans on, cannot see a damaged sidecar the store does
    not report.
    """
    store = _write(tmp_path, "\n".join([
        "schema: []",
        "nodes:",
        "  raiz:",
        "    title: Raiz",
        "  fantasma:",
        "    title: No existe en el mmd",
        "  segundo_fantasma:",
        "    title: Tampoco existe",
        "",
    ]))
    graph = store.load("m")

    # SET EQUALITY, not per-phantom membership. `LLR-REPAIR.1`'s restated
    # threshold says "the set of named ids shall equal the set of phantoms --
    # set equality, not a count", and the first version of this arm used `any()`
    # per phantom, which cannot see an implementation that names EVERY id.
    named = {
        w.split("'")[1] for w in graph.load_warnings
        if w.startswith("nodo fantasma:")
    }
    assert named == {"fantasma", "segundo_fantasma"}, (
        f"the named phantoms are {named}; the sidecar's phantoms are "
        f"{{'fantasma', 'segundo_fantasma'}}. Warnings: {graph.load_warnings}"
    )
    # AND THE WARNING MUST NOT CHANGE WHAT THE MAP IS. `LLR-REPAIR.1` says the
    # store shall warn "and shall not change the meaning of the coverage values
    # it returns", so the phantom is REPORTED, not REMOVED -- dropping it would
    # move `coverage()`'s denominator, which is the one thing the requirement
    # forbids.
    #
    # The first version of this arm asserted the phantom was ABSENT. That was my
    # over-specification, not the requirement's: it contradicted the clause it
    # was written to enforce, and the fix made it fail. Reported-not-removed is
    # the whole point -- a warning that silently changed the arithmetic would be
    # a second defect wearing the first one's fix.
    assert "fantasma" in graph.nodes
    assert set(graph.nodes) == {"raiz", "hijo", "fantasma", "segundo_fantasma"}


def test_at049_a_clean_sidecar_records_no_phantom(tmp_path):
    """`AT-049`'s NEGATIVE arm, mandated verbatim by the boundary catalog.

    §3.9 requires it: "drives the same workspace with the phantom removed and
    asserts NO warning and a healthy card, so the positive arm is not passing on
    a constant." It was not written, and the code review fired what that costs:
    moving the `append` out of its `if nid not in graph.nodes:` guard -- one
    indentation level, and the shape an implementer reaches for -- makes the
    store warn for EVERY sidecar id, so every healthy map raises a toast naming
    each node. All seven arms stayed green.

    A positive arm alone cannot tell "names the phantoms" from "names
    everything".
    """
    store = _write(tmp_path, "\n".join([
        "schema: []",
        "nodes:",
        "  raiz:",
        "    title: Raiz",
        "  hijo:",
        "    title: Hijo",
        "",
    ]))
    graph = store.load("m")

    assert [w for w in graph.load_warnings if "fantasma" in w] == [], (
        "a sidecar whose ids all exist in the .mmd raised a phantom warning: "
        f"{graph.load_warnings}"
    )
    assert set(graph.nodes) == {"raiz", "hijo"}


# ---------------------------------------------------------------------------
# AT-050 / LLR-REPAIR.2 / B-30


def test_at050_a_not_found_message_names_the_map_not_the_filesystem(tmp_path):
    """The message names the MAP. It must not disclose the filesystem.

    Measured pre-fix: `Map not found: <absolute path>\\no_such_map.mmd` -- the
    full path including the operator's home directory. That string reaches the
    `load_or_notice` toast, so it is operator-visible and screenshot-visible.
    """
    store = MapStore(tmp_path)
    with pytest.raises(MapStoreError) as caught:
        store.load("no_such_map")
    message = str(caught.value)

    assert "no_such_map" in message, (
        f"the message must name the map the operator asked for: {message!r}"
    )
    assert str(tmp_path) not in message, (
        f"the message discloses the workspace path: {message!r}"
    )
    # `LLR-REPAIR.2`'s second numeric clause, which was not asserted: the id
    # appears EXACTLY ONCE. A message that named it twice, or that appended a
    # workspace component, would pass a mere containment check.
    assert message.count("no_such_map") == 1, (
        f"the map id appears {message.count('no_such_map')} times: {message!r}"
    )
    for marker in ("\\", "/", ".mmd"):
        assert marker not in message, (
            f"the message carries a filesystem detail {marker!r}: {message!r}"
        )


def test_at050_the_message_discloses_no_workspace_component(tmp_path):
    """`AT-050`'s boundary arm: a SENTINEL, not a separator.

    The arm above asserts no `/` or `` appears, and that proxy does not
    generalise -- a map id the operator typed as `sub/dir/mapa` puts a separator
    in the message legitimately, and the arm would call the store guilty for
    echoing what it was asked for. The requirement's oracle is whether a
    WORKSPACE COMPONENT leaks, so the workspace is given a component that cannot
    appear by coincidence.
    """
    marker = "zzsentinelzz"
    workspace = tmp_path / marker
    workspace.mkdir()
    store = MapStore(workspace)

    with pytest.raises(MapStoreError) as caught:
        store.load("no_such_map")
    message = str(caught.value)

    assert marker not in message, (
        f"the message discloses a workspace path component: {message!r}"
    )
    assert "no_such_map" in message


# ---------------------------------------------------------------------------
# B-48 — the attachments phantom


def test_b48_a_mapping_without_attachment_keys_is_refused_not_invented(tmp_path):
    """`attachments` validates TYPE but not CONTENT.

    A scalar entry is correctly refused with a warning. A MAPPING carrying none
    of the attachment keys is accepted SILENTLY as an `Attachment` with empty
    kind, path and caption -- so nothing is lost and a phantom is INVENTED.

    `store.py`'s own comment records that malformed attachments used to be
    discarded silently and that this was fixed. The fix covered scalars and not
    mappings, which is a declaration outrunning the code.

    THE REFUSAL IS KEY-BASED, AND THIS ARM'S FIRST CLAIM WAS CONTENT-BASED.
    A hand-written `kind: null / path: null / caption: null` still yields an
    Attachment with three empty strings -- the reviewer fired it -- and that is
    CORRECT: those keys are an operator's deliberately-empty attachment, and
    refusing on emptiness would destroy it on the next save. What is refused is
    a mapping sharing NONE of the attachment keys. The arm's fixture happens to
    use an unknown key, so the original wording ("no empty attachment survives")
    was true of the fixture and false of the rule.
    """
    store = _write(tmp_path, "\n".join([
        "schema: []",
        "nodes:",
        "  raiz:",
        "    title: Raiz",
        "    attachments:",
        "      - title: soy-un-nodo-no-un-adjunto",
        "      - 42",
        "",
    ]))
    graph = store.load("m")
    attachments = graph.nodes["raiz"].ficha.attachments

    # The scalar is already refused -- the control that shows the arm is not
    # asserting a blanket "nothing is ever accepted".
    assert any("attachments[1]" in w for w in graph.load_warnings), (
        "the scalar entry should already be refused with a coordinate; if this "
        f"fails the fixture no longer exercises the asymmetry. {graph.load_warnings}"
    )
    assert attachments == [], (
        f"{len(attachments)} attachment(s) were INVENTED from a mapping sharing "
        "none of the attachment keys. Neither entry in this fixture names kind, "
        f"path or caption. Warnings: {graph.load_warnings}"
    )
    assert any("adjunto sin campos" in w for w in graph.load_warnings), (
        f"the mapping was dropped without a record: {graph.load_warnings}"
    )


# ---------------------------------------------------------------------------
# LLR-N13.1.7 — alias amplification, by STRUCTURE not by clock


def test_llr_n13_1_7_refusal_warnings_carry_coordinates_not_values(tmp_path):
    """THE MESSAGE REPORTING THE REFUSAL MUST NOT PERFORM THE MATERIALISATION.

    The per-key coercion DOES refuse an alias-amplified value -- `campo ilegible:
    document[0].name` is emitted and the name is coerced to `''`. The duplicate
    branch then interpolates the RAW, UNCOERCED value with `!r`, which
    materialises the very structure the refusal prevented.

    THE ORACLE IS THE MESSAGE'S SIZE, NOT THE CLOCK. That is what makes this arm
    deterministic and cheap: warning length grows 10x per amplification level
    while wall time barely moves at shallow depths, so the default lane carries
    no wall-clock assert (`FLAKE-1` is what that discipline is for).

    THE NUMBERS, EACH ATTACHED TO THE TREE IT WAS MEASURED ON. On the SHIPPED
    tree the benign fixture is 31 chars and five levels is 107 -- 19x UNDER the
    2,000 bound, which is what a green arm should look like. With the defect
    REINTRODUCED, five levels emits 522,311 chars: red by 261x for the price of
    a cheap fixture, which is why five is the level driven.

    That 522,311 decomposes, and I checked it rather than inheriting it: the
    materialised duplicate record is 522,247 chars and the two `campo ilegible:
    document[i].name` records are 32 each. Only the SECOND half of the duplicate
    record was ever raw -- `doc.name` is the value the per-key coercion already
    replaced with `''` -- so interpolating both halves raw reproduces a defect
    that never shipped and doubles the figure to 1,044,465.

    The first version of this docstring put "measured on the shipped tree" in
    front of the 522,311 -- a pre-fix figure. The first CORRECTION added the
    distinction at the top and left the old conclusion standing at the bottom,
    so the text asserted both "19x under its bound" and "RED by four orders of
    magnitude" four lines apart. A docstring that contradicts itself is not a
    corrected one.
    """
    graph = _write(tmp_path, amplified(levels=5)).load("m")
    total = sum(len(w) for w in graph.load_warnings)

    # POSITIVE CONTROL FIRST. This arm is a pure UPPER bound, so deleting the
    # diagnostic entirely is a green way to pass it -- fired and confirmed by
    # the code review. The record must exist before its size is judged.
    assert any(w.startswith("documento duplicado:") for w in graph.load_warnings), (
        f"the duplicate record is missing entirely: {graph.load_warnings}"
    )
    assert total < 2_000, (
        f"the load warnings total {total:,} characters. A diagnostic that "
        "embeds the refused VALUE materialises the structure the refusal "
        "prevented; every other warning in this module names a COORDINATE."
    )


# THE AST "CLASS" ARM WAS DELETED (`Inc-REPAIR` S-E review, MEDIUM-1).
#
# It forbade `!r` applied to a `Call`, and its docstring claimed "the defect
# cannot be rewritten elsewhere". The reviewer rewrote it TWICE and the arm
# stayed green: `d['name']!r` is a Subscript, a name bound to raw data is a
# Name, and `doc.name!r` -- WHICH WAS LIVE ON THE SAME LINE -- is an Attribute.
# `ast.Call` is one spelling of four, and `f"{repr(x)}"` uses no conversion at
# all.
#
# It was shape-based where the property is semantic, so it passed the fix and
# the reintroduced defect for the same reason. The structural arm below killed
# both rewrites at 261x in 0.02 s. An arm that names a class it does not cover
# is worse than no arm: it reads as coverage.


def scalar_amplified(payload: int = 50_000, dups: int = 200) -> str:
    """ONE anchor reused across many duplicate names -- no alias DEPTH at all.

    The code review fired this and it is worse than the bomb it replaced: a
    57 KB sidecar produced 19.9 MB of warnings in 0.081 SECONDS -- 348x
    amplification and CHEAP, so nothing times out. A type bound let it through
    because a huge `str` is an allowed type.
    """
    lines = ["_anchors:", f"  big: &big {'x' * payload}", "schema: []", "documents:"]
    for _ in range(dups):
        lines += ["  - name: *big", "    path: p.pdf"]
    lines += ["nodes:", "  raiz:", "    title: benigno", ""]
    return "\n".join(lines)


def test_llr_n13_1_7_a_huge_scalar_origin_is_bounded_too(tmp_path):
    """A TYPE bound is not a LENGTH bound.

    `_raw_origin` first admitted any scalar, and `AT-P02d` needs the origin
    shown so a coercion collision is distinguishable -- so the answer is
    truncation, not removal. Both halves of the record are bounded: `doc.name!r`
    was unbounded too, and being an Attribute rather than a Call, no AST arm
    shaped around `{call()!r}` could see it.
    """
    graph = _write(tmp_path, scalar_amplified()).load("m")

    assert any(w.startswith("documento duplicado:") for w in graph.load_warnings), (
        f"the duplicate record is missing entirely: {graph.load_warnings[:2]}"
    )
    total = sum(len(w) for w in graph.load_warnings)
    assert total < 200_000, (
        f"a 57 KB sidecar produced {total:,} characters of warnings. These are "
        "joined and coerced into an operator toast, so a megabyte of them is a "
        "per-character translate on the way to the screen."
    )


# THE SLOW TIMING ARM WAS DELETED (`Inc-REPAIR` S-E review, LOW-1).
#
# It asserted `elapsed < 5.0` on an 8-level sidecar. Fired, the mutants that
# reintroduce the defect reddened it at 5.0 s and 5.2 s -- a 0-4% margin, which
# on a faster machine or a warm cache goes GREEN against the defect it exists
# for. My own note called it "marginally red"; the measurement says that
# understated it.
#
# Neither alternative works: 9 levels is 54 s and falsifies `pyproject.toml`'s
# own declaration that no arm in either lane exceeds 20 s, and this defect's
# cost curve offers no point in between. A wall-clock arm should be reddened by
# an order of magnitude, not by 0.4%.
#
# The structural arm above kills the same mutants at 261x in 0.02 s,
# deterministically, in the DEFAULT lane. Keeping a weaker duplicate in a lane
# that runs less often is how a suite acquires arms nobody trusts.


def attachment_amplified(id_len: int = 1_000, aliases: int = 400) -> str:
    """A long node id reused across many aliased attachment entries.

    THE STAGE'S OWN FIX INTRODUCED THIS LINE. `adjunto sin campos:
    {owner}.{key}[{i}]` reads like a coordinate and carries a VALUE -- `owner` is
    the node id, read from the sidecar. The security review measured the
    unbounded form at 2.0 GB of records in 0.84 s, 9,092x amplification: 26x
    larger than the alias bomb this stage was repairing and 60x CHEAPER, so
    nothing times out.

    THE ID IS 1,000 CHARS, NOT THE REVIEW'S 100,000, AND THE REASON IS A LIMIT
    I MEASURED RATHER THAN A CHOICE: PyYAML's scanner refuses a mapping key much
    past 1 KB -- `mapping values are not allowed here` -- quoted or not, at
    20,000 and at 100,000. So a node id cannot reach `owner` at that length
    through a mapping key, and I could not reproduce the review's id length by
    this route. The AMPLIFICATION does not depend on it: record COUNT is the
    other free variable and it is file-linear, so the fixture buys its size in
    aliases instead.
    """
    big = "z" * id_len
    lines = ["_anchors:", "  bad: &bad", "    z: 1", "schema: []", "nodes:",
             f'  "{big}":', "    title: benigno", "    attachments:"]
    lines += ["      - *bad"] * aliases
    lines.append("")
    return "\n".join(lines)


def test_llr_n13_1_7_a_coordinate_that_carries_a_value_is_bounded_too(tmp_path):
    """A coordinate is not automatically short.

    Every other record in `store.py` names a position and is short by
    construction. This one interpolates `owner`, a sidecar-supplied node id, so
    it reads like a coordinate and behaves like a value -- which is how the fix
    for a materialisation defect shipped a worse one.

    Both free variables are bounded now: per-record length and record COUNT,
    because 5 bytes of sidecar buys another record and the list is joined into
    an operator toast before anything else sees it.
    """
    graph = _write(tmp_path, attachment_amplified()).load("m")

    assert any("adjunto sin campos" in w for w in graph.load_warnings), (
        f"the refusal record is missing entirely: {graph.load_warnings[:2]}"
    )
    total = sum(len(w) for w in graph.load_warnings)
    assert total < 200_000, (
        f"this sidecar produced {total:,} characters of records. The security "
        "review measured the unbounded form at 20,107,707 characters on a "
        "101 KB file, of which 99.5% came from this one line."
    )
    assert len(graph.load_warnings) <= 210, (
        f"{len(graph.load_warnings)} records; the count is file-linear and must "
        "be capped before the join, not at it"
    )


# ---------------------------------------------------------------------------
# The coercion sink beside it


@pytest.mark.asyncio
async def test_the_coverage_cell_does_not_parse_markup_from_a_ficha_title(tmp_path):
    """THE ARM THE `Text(...)` FIX SHIPPED WITHOUT -- reading the REAL cell.

    The code review's condition was the wrap AND an arm; only the wrap landed.
    The security review then fired the wrap's removal against the whole suite:
    997 passed, NOT ONE ARM MOVED, while the same mutant emits an OSC-8
    hyperlink to the terminal and crashes the app on `[/]`.

    MY FIRST VERSION OF THIS ARM ALSO SURVIVED THAT MUTANT, and the reason is
    worth the space: it built the cell itself -- `Text(darkside.plain(hostile))`
    -- so it asserted a property of an expression it had written, not of the one
    `coverage.py` passes. A parallel fiction, which is the same failure this
    batch named for the `AT-058` absent-state arm. An arm that constructs its own
    subject cannot see the call site change.

    So this drives the real `CoverageScreen`, pulls what the table was actually
    handed, and asserts the property there.
    """
    from textual.app import App
    from textual.widgets import DataTable

    from mapper.model import Edge, Ficha, Graph, Node, SchemaField
    from mapper.screens.coverage import CoverageScreen

    hostile = "[red]rojo[/red] [link=file:///etc/passwd]click[/link]"
    graph = Graph()
    graph.schema = [SchemaField(key="D", label="documento", required=True)]
    graph.add_node(Node(id="root", ficha=Ficha(title="Raiz", fields={"D": "x"})))
    graph.add_node(Node(id="malo", ficha=Ficha(title=hostile)))
    graph.add_edge(Edge("root", "malo"))

    class _Host(App):
        def on_mount(self) -> None:
            self.push_screen(CoverageScreen(graph, "m"))

    async with _Host().run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        table = pilot.app.screen.query_one(DataTable)
        row = table.get_row_at(0)

    cell = next(
        (c for c in row if hasattr(c, "plain") and "rojo" in c.plain), None
    )
    assert cell is not None, f"the hostile title is not in the row: {row}"
    assert cell.spans == [], (
        f"the cell carries {len(cell.spans)} style span(s) from a ficha title: "
        f"{cell.spans}. A sidecar is choosing the styling, and a `link` span "
        "reaches the terminal as OSC-8."
    )
    assert "[red]" in cell.plain, (
        "the markup must survive as LITERAL TEXT, not be interpreted away"
    )


@pytest.mark.asyncio
async def test_an_unbalanced_closing_tag_in_a_title_does_not_kill_the_screen():
    """A SEPARATE arm, because `[/]` is a separate FAILURE MODE.

    The arm above catches a leaked style span -- an integrity defect. This one
    catches a crash: an unbalanced closing tag in a sidecar title raises
    `MarkupError` from inside `DataTable._on_idle`, which is **not** on a path
    the screen can guard; it is the compositor's own reflow. `escape` prevented
    it before the swap, `plain` alone did not, and `Text(...)` does -- which is
    what makes the shipped fix an AVAILABILITY fix as well as an integrity one.

    Asserting `spans == []` cannot see this: a crashing render never reaches the
    assert. So the two arms are not redundant, and neither subsumes the other.
    """
    from textual.app import App
    from textual.widgets import DataTable

    from mapper.model import Edge, Ficha, Graph, Node, SchemaField
    from mapper.screens.coverage import CoverageScreen

    graph = Graph()
    graph.schema = [SchemaField(key="D", label="documento", required=True)]
    graph.add_node(Node(id="root", ficha=Ficha(title="Raiz", fields={"D": "x"})))
    graph.add_node(Node(id="malo", ficha=Ficha(title="acta firmada[/]")))
    graph.add_edge(Edge("root", "malo"))

    class _Host(App):
        def on_mount(self) -> None:
            self.push_screen(CoverageScreen(graph, "m"))

    async with _Host().run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        table = pilot.app.screen.query_one(DataTable)
        row = table.get_row_at(0)

    cell = next((c for c in row if hasattr(c, "plain") and "acta" in c.plain), None)
    assert cell is not None, f"the title is not in the row: {row}"
    assert cell.plain == "acta firmada[/]", (
        f"the closing tag did not survive as literal text: {cell.plain!r}"
    )


def test_coverage_screen_coerces_file_derived_text_with_plain():
    """`screens/coverage.py` used `escape`, and `escape` COERCES NOTHING.

    This batch measured that at `Inc-CRUMB`: four crumb producers reached the
    frame under `escape` alone, which guards markup and passes control
    characters, bidi overrides and zero-width joiners untouched. The standard is
    `darkside.plain`.

    Structural rather than behavioural because the claim is about which sink the
    module uses, and a rendered-frame assertion would pass the day someone adds
    a second unescaped call site beside a coerced one.
    """
    import mapper.screens.coverage as cov

    tree = ast.parse(Path(cov.__file__).read_text(encoding="utf-8"))
    escapes = [
        node.lineno for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "escape"
    ]
    assert not escapes, (
        f"coverage.py calls escape() at line(s) {escapes}. escape() guards "
        "markup and coerces nothing -- use darkside.plain, which this batch "
        "settled as the standard for file-derived text."
    )
