"""`LLR-N16.2.1` — the declaration is DERIVED from `01b`, not transcribed.

THIS FILE EXISTS BECAUSE ITS ABSENCE WAS A LIE. `darkside.DECLARED_VOCABULARY`'s
docstring claimed "`tests/test_home.py` DERIVES from that document and compares,
so this table is a declaration to be checked" -- and no such comparison existed
anywhere in `tests/`. **A DECLARATION WEARING A CHECK'S CLOTHES.** Measured
consequence: the hand-transcribed table drifted in at least six rows against
`01b`, two of them FABRICATIONS -- `V7` and `V8` were given glyphs the document
does not assign and a label that appears nowhere in it.

So the remedy is not to re-transcribe more carefully. That method has now
produced errors once, and carefully is not a mechanism. The table is DERIVED
here, from the artifact that owns it.

THE GLYPH IS A SET, per `01b` Amendment 2(b): some members are one character and
some are a RANGE used as one device (a braille field is a single visual form
whose codepoint varies with the data). Membership reads "the painted codepoint is
in the declared glyph set for that meaning".
"""
from __future__ import annotations

import pathlib
import re

from mapper import darkside
from mapper.screens import help as help_screen

UX = (pathlib.Path(__file__).resolve().parent.parent / ".dev-flow"
      / "2026-08-26-ui-next-batch-02" / "01b-ux-decisions.md")

# A row id MAY CARRY A LETTER SUFFIX. `(V\d+)` -- digits only -- silently skipped
# `V4a` and `V4b` and produced the fifth wrong generation of this count. The same
# defect broke an `AT-[0-9]{3}` census in this project months earlier, so
# SUFFIXED IDS ARE A NAMED HAZARD: derive the pattern from the id GRAMMAR rather
# than assuming digits.
ROW = re.compile(r"^\|\s*(V\d+[a-z]?)\s*\|(.+?)\|(.+?)\|(.+?)\|", re.M)
STYLE = re.compile(r"`(?:bold\s+)?[A-Z][A-Z_]*(?:\s+on\s+[A-Z][A-Z_]*)?`")

# `INC7-CR-R3-F1`'s anchor: the LITERAL id cell `V22`, not a digit pattern.
# `ROW` above is already suffix-aware for the general walk, but this
# derivation exists for exactly one row, so it names that row rather than
# re-deriving it through a pattern built for many.
_V22_ROW = re.compile(r"^\|\s*V22\s*\|(.*?)\|", re.M)
_BACKTICK_TOKEN = re.compile(r"`([^`]+)`")


def _unwrap(cell: str) -> str:
    """Strip ONLY a pair of backticks wrapping the WHOLE cell.

    A blind `.strip("`")` ate the closing backtick of `V21`'s label while this
    instrument was being written -- a transcription defect inside the very
    instrument built to catch transcription defects.
    """
    s = cell.strip()
    return s[1:-1] if len(s) >= 2 and s.startswith("`") and s.endswith("`") else s


def _section() -> str:
    txt = UX.read_text(encoding="utf-8")
    return txt[txt.index("### 3.1 "):txt.index("### 3.5 ")]


def derived_rows() -> list[tuple[str, str, str, str]]:
    rows = ROW.findall(_section())
    assert rows, "the row walk derived NOTHING; the instrument is broken, not the document"
    return rows


def _v22_glyph_cell_from_01b() -> str:
    """`INC7-CR-R3-F1`: read `01b`'s OWN row for `V22`, independently of
    `darkside`.

    Bytes, decoded UTF-8 explicitly, anchored on the literal id cell `V22`
    rather than the general suffix-aware pattern above -- this derivation has
    exactly one row to find, so it names that row instead of walking for it.
    A missing row fails loudly here, not silently.
    """
    text = UX.read_bytes().decode("utf-8")
    match = _V22_ROW.search(text)
    assert match, "row `V22` (literal id) is not in 01b -- nothing to derive from"
    return match.group(1)


def _first_backtick_token(cell: str) -> str:
    """The first backtick-quoted token in *cell*, failing loudly if absent
    or empty rather than returning something that compares equal by accident.
    """
    match = _BACKTICK_TOKEN.search(cell)
    assert match, f"no backtick-quoted token in the cell: {cell!r}"
    token = match.group(1)
    assert token, f"the backtick-quoted token in {cell!r} is empty"
    return token


def test_llr_n16_2_1_the_instrument_finds_the_suffixed_rows():
    """The guard on every arm below, and it is the defect that produced a wrong count.

    A digits-only id pattern passes silently -- it returns rows, just not all of
    them -- so nothing downstream can tell it failed. This asserts the hazard
    directly rather than trusting the regex.
    """
    ids = [r[0] for r in derived_rows()]
    # The Inc-8 design pass retired `V4a` and split `V21` into `V21a`/`V21b`;
    # the hazard's known suffixed members are now these three.
    assert {"V4b", "V21a", "V21b"} <= set(ids), (
        f"the suffixed rows are missing from the derivation: {ids}"
    )
    assert len(ids) == len(set(ids)), f"duplicate row ids in the derivation: {ids}"


def test_llr_n16_2_1_the_D7_removal_step_HAS_A_SUBJECT():
    """`01b` Amendment 2(a): the marker was intended, read for, and never written.

    The instrument says to remove every row carrying `DEFERRED(#D7)`. Until that
    amendment **no row carried it**, so the step removed nothing and every
    derivation relying on it was wrong. This arm fails if the marker ever
    disappears again, which is the only way to keep an inert step from silently
    returning to being inert.
    """
    marked = [r[0] for r in derived_rows() if "DEFERRED(#D7)" in "".join(r)]
    assert marked, (
        "no row carries DEFERRED(#D7), so the removal step is INERT and any count "
        "derived through it is wrong"
    )
    assert "V18" in marked, f"#D7 marks rows {marked}; V18 is the one it rules out"


def test_llr_n16_2_1_every_declared_row_is_FAITHFUL_to_the_document():
    """The arm the docstring claimed existed. It did not, and the table drifted.

    FAITHFULNESS, NOT SET EQUALITY: every row the product declares appears in
    `01b` with that style. **Fabrication is what it catches**, and fabrication is
    what happened. Set equality, which Inc-8 owed, is
    `test_inc7_cr_r2_f3_the_declaration_EQUALS_the_document` below.
    """
    rows = derived_rows()
    doc_styles: dict[str, set[str]] = {}
    for _vid, _glyph, label, style_cell in rows:
        lab = _unwrap(label)
        for st in STYLE.findall(style_cell):
            doc_styles.setdefault(lab, set()).add(st.strip("`"))

    unfaithful = []
    for _vid, _glyph, label, style in darkside.DECLARED_VOCABULARY:
        if label not in doc_styles:
            unfaithful.append((label, style, "LABEL APPEARS NOWHERE IN 01b"))
        elif style not in doc_styles[label]:
            unfaithful.append(
                (label, style, f"01b gives {sorted(doc_styles[label])}")
            )
    assert not unfaithful, (
        "rows in DECLARED_VOCABULARY that 01b does not support:\n  "
        + "\n  ".join(f"{lab!r} declared {st!r} -- {why}" for lab, st, why in unfaithful)
    )


def test_llr_n16_2_1_the_damaged_map_row_is_declared_and_not_deferred():
    """`PRED-VIS`'s membership clause has a live subject, and it is not `#D7`-removed."""
    rows = derived_rows()
    v22 = [r for r in rows if r[0] == "V22"]
    assert v22, "V22 is missing from 01b; PRED-VIS has nothing to draw from"
    assert "DEFERRED(#D7)" not in "".join(v22[0]), "V22 is marked deferred"
    declared = {vid: glyph for vid, glyph, _l, _s in darkside.DECLARED_VOCABULARY}
    assert "V22" in declared, "V22 is in 01b but not in the declaration"
    assert declared["V22"] == darkside.DAMAGED_MAP_GLYPH, (
        f"V22's declared glyph set is {declared['V22']!r}, not the glyph the card "
        f"paints ({darkside.DAMAGED_MAP_GLYPH!r}). THIS PIN EXISTS BECAUSE THE "
        f"EXTRACTOR GOT IT WRONG: V22's cell quotes the whole card string after "
        f"its glyph, and a blind sweep of the cell pulled the accents out of that "
        f"prose into the glyph set."
    )

    # `INC7-CR-R3-F1`: the assert above is CONSTANT AGAINST CONSTANT --
    # `declared["V22"]` comes from `DECLARED_VOCABULARY` and
    # `darkside.DAMAGED_MAP_GLYPH` from the same module, so the two drifting
    # TOGETHER away from `01b` left it green (mutant E: both changed to `X`).
    # This derives the glyph from `01b`'s own row text, independently of
    # anything `darkside` declares about itself.
    doc_glyph = _first_backtick_token(_v22_glyph_cell_from_01b())
    assert doc_glyph == darkside.DAMAGED_MAP_GLYPH, (
        f"01b's V22 row gives the glyph {doc_glyph!r} but "
        f"darkside.DAMAGED_MAP_GLYPH is {darkside.DAMAGED_MAP_GLYPH!r} -- one "
        f"of the two drifted, either from the other or from 01b itself"
    )


# ---------------------------------------------------------------------------
# Inc-8 -- `INC7-CR-R2-F2` (the glyph column, derived by a WRITTEN RULE) and
# `INC7-CR-R2-F3` (completeness: set EQUALITY, not faithfulness).

_CHIP = re.compile(r"legend chip\s+`([^`]+)`")
_EXAMPLE = re.compile(r"e\.g\.\s+`([^`]+)`")
_LEADING_TOKEN = re.compile(r"`([^`]+)`")
_PLACEHOLDER = re.compile(r"<[^>]+>")
_RANGE = re.compile(r"`U\+([0-9A-F]{4,6})`\s*[–-]\s*`U\+([0-9A-F]{4,6})`")
#: `INC8-F-CR-F3`: a glyph cell may name its set character by character --
#: `glyph set `─│┌┐``` -- and each character is a one-codepoint range.
_GLYPH_SET = re.compile(r"glyph set\s+`([^`]+)`")
_QUALIFIER = re.compile(r"([a-z]+)\s")
_STYLE_TOKEN = re.compile(r"`((?:bold\s+)?[A-Z][A-Z_]*(?:\s+on\s+[A-Z][A-Z_]*)?)`")

#: Rows whose glyph cell is PROSE: the rule derives no sample, the declaration
#: carries `""`, and each is an open question for the operator.  EMPTY since
#: the Inc-8 design pass: `V4b` gained a real braille sample (verdict `Q1`/`Q2`)
#: and `V12` is deferred with the lens (`Q4`).  Pinned so a new prose cell
#: reddens instead of shipping an empty sample.
OPERATOR_QUESTIONS: set[str] = set()

#: `01b` DECISION 3's fifth column, which names the legend(s) painting a row.
_VIEWS_ROW = re.compile(r"^\|\s*(V\d+[a-z]?)\s*\|(?:[^|]*\|){3}([^|]*)\|", re.M)
_RETIRED = re.compile(r"^\|\s*`(V\d+[a-z]?)`\s*\|[^|]*\|\s*\*\*RETIRED\*\*", re.M)


def _leading_run(cell: str) -> list[str]:
    """The backtick tokens that open the cell, separated only by whitespace."""
    rest, run = cell.strip(), []
    while (m := _LEADING_TOKEN.match(rest)):
        run.append(m.group(1))
        rest = rest[m.end():]
        if not rest.startswith(" ") or not rest.lstrip().startswith("`"):
            break
        rest = rest.lstrip()
    return run


def sample_by_style(glyph_cell: str, style_cell: str) -> dict[str, str | None]:
    """THE GLYPH RULE (`INC7-CR-R2-F2`) -- what the legend paints for each style.

    Applied in order; the first that yields wins:

    G1  LEGEND CHIP.  The cell names the legend's own form (`legend chip `X``):
        that token, for every style of the row.  (No live row uses it since
        the Inc-8 design pass; `V18`'s cell still carries one, and `V18` is
        `DEFERRED(#D7)`.)
    G2  QUALIFIED PAIRS.  The style cell has several `;`-separated segments,
        each opening with a qualifier word, and the glyph cell pairs a token
        with each of those words (`` `█` con acta ``): each style takes the
        token of the qualifier its segment opens with.  (`V19`, `V40`, and
        `V3`'s `bar` / `pill`)
    G3  LEADING RUN.  The backtick tokens opening the cell, whitespace-separated,
        joined with one space; a token with a `<placeholder>` is a TEMPLATE and
        is dropped, and if nothing remains the `e.g.` token stands in.  Prose
        after the run (a parenthetical) is a GLOSS, not glyph.
        (`V31` -> `▽ 35 fuera de vista`, `V27` -> `D✓`)
    G4  NOTHING.  A cell with no token is prose: `None`, and an operator
        question -- never a guess.  (No declared row since the Inc-8 design
        pass; `V12`'s bare-title cell would be one, and it is deferred.)

    Codepoint RANGES (`` `U+2800`–`U+28FF` ``) and GLYPH SETS
    (`` glyph set `─│┌┐` ``) are read separately by `_RANGE` and `_GLYPH_SET`;
    they widen the glyph SET (Amendment 2(b)) and never become the sample.
    """
    styles = _STYLE_TOKEN.findall(style_cell)
    chip = _CHIP.search(glyph_cell)
    if chip:
        return {st: chip.group(1) for st in styles}
    segments = [s.strip() for s in style_cell.split(";")]
    if len(segments) >= 2 and all(_QUALIFIER.match(s) for s in segments):
        paired: dict[str, str | None] = {}
        for segment in segments:
            word = _QUALIFIER.match(segment).group(1)
            token = re.search(r"`([^`]+)`\s+" + re.escape(word) + r"\b", glyph_cell)
            if not token:
                break
            for st in _STYLE_TOKEN.findall(segment):
                paired[st] = token.group(1)
        else:
            return paired
    run = [t for t in _leading_run(glyph_cell) if not _PLACEHOLDER.search(t)]
    if not run and (example := _EXAMPLE.search(glyph_cell)):
        run = [example.group(1)]
    sample = " ".join(run) if run else None
    return {st: sample for st in styles}


def _views_by_row() -> dict[str, set[str]]:
    """Row id -> the views its `01b` Views column names (`atlas · esquema`)."""
    out: dict[str, set[str]] = {}
    for vid, cell in _VIEWS_ROW.findall(_section()):
        out[vid] = {v.strip() for v in cell.split("·") if v.strip() not in ("", "—")}
    return out


def _retired_ids() -> set[str]:
    """The ids the change log above §3.1 marks **RETIRED**."""
    text = UX.read_bytes().decode("utf-8")
    log = text[text.index("## DECISION 3 "):text.index("### 3.1 ")]
    return set(_RETIRED.findall(log))


def derived_members() -> tuple[set[tuple[str, str, str, str]], dict[str, set[tuple[int, int]]]]:
    """`LLR-N16.2.1`'s instrument, run: `01b` §3.1-3.4 -> the declared members.

    One member per distinct triple (`A-103`), the first id naming it keeps it
    (`V4a` collapses into `V4`), `DEFERRED(#D7)` rows contribute nothing, and a
    row's ranges attach to the member it collapsed into.
    """
    members: dict[tuple[str, str, str], str] = {}
    ranges: dict[str, set[tuple[int, int]]] = {}
    for vid, glyph_cell, label_cell, style_cell in derived_rows():
        if "DEFERRED(#D7)" in glyph_cell + label_cell + style_cell:
            continue
        for style, sample in sample_by_style(glyph_cell, style_cell).items():
            owner = members.setdefault((sample or "", _unwrap(label_cell), style), vid)
            for lo, hi in _RANGE.findall(glyph_cell):
                ranges.setdefault(owner, set()).add((int(lo, 16), int(hi, 16)))
            for chars in _GLYPH_SET.findall(glyph_cell):
                ranges.setdefault(owner, set()).update((ord(c), ord(c)) for c in chars)
    return {(vid, g, lab, st) for (g, lab, st), vid in members.items()}, ranges


def test_inc7_cr_r2_f3_the_declaration_EQUALS_the_document():
    """`INC7-CR-R2-F3`: SET EQUALITY in both directions, id included.

    Faithfulness (above) caught fabrication only: dropping a row, or renaming
    its id, stayed green.  Equality over the full 4-tuple reddens both.
    """
    declared = list(darkside.DECLARED_VOCABULARY)
    assert len(declared) == len(set(declared)), "a member is declared twice"
    derived, _ = derived_members()
    missing = sorted(derived - set(declared))
    extra = sorted(set(declared) - derived)
    assert not missing and not extra, (
        f"01b derives members the declaration lacks: {missing}\n"
        f"the declaration carries members 01b does not derive: {extra}"
    )


def test_inc7_cr_r2_f2_every_glyph_follows_the_written_rule_row_by_row():
    """`INC7-CR-R2-F2`, row by row, as `V22`'s pin does for one row.

    Reported per (id, style) so a drifted glyph names its row rather than
    surfacing as one opaque set difference.
    """
    derived, _ = derived_members()
    want = {(vid, st): g for vid, g, _lab, st in derived}
    got = {(vid, st): g for vid, g, _lab, st in darkside.DECLARED_VOCABULARY}
    drift = sorted((k, got.get(k), want[k]) for k in want if got.get(k) != want[k])
    assert not drift, "glyphs that do not follow the rule:\n  " + "\n  ".join(
        f"{vid}/{st}: declared {g!r}, rule gives {w!r}" for (vid, st), g, w in drift
    )


def test_inc7_cr_r2_f2_the_rule_leaves_exactly_the_operator_questions_open():
    """G4 is a question, not a default: the undecidable rows are pinned."""
    undecided = {vid for vid, g, _lab, _st in derived_members()[0] if not g}
    assert undecided == OPERATOR_QUESTIONS, undecided


def test_every_declared_range_EQUALS_the_document():
    """`01b` Amendment 2(b): a glyph may be a SET with a range.

    Verdict `Q1`/`Q2`: the braille range left `V4` (retired) and belongs to
    radial's edge row `V4b`, which also gained a real braille sample.
    """
    _, ranges = derived_members()
    assert {k: set(v) for k, v in darkside.DECLARED_GLYPH_RANGES.items()} == ranges
    assert (0x2800, 0x28FF) in ranges["V4b"], ranges
    assert "V4" not in ranges
    v4b = {g for vid, g, _l, _s in darkside.DECLARED_VOCABULARY if vid == "V4b"}
    assert v4b and all(0x2800 <= ord(c) <= 0x28FF for g in v4b for c in g), v4b


def test_inc8_f_cr_f3_V29_owns_exactly_the_wires_the_canvas_paints():
    """`INC8-F-CR-F3`: `V29` owned the whole box-drawing block, so a canvas
    that started painting `╳` was already "explained".  Its set is now the
    canvas's own wire table, read from `mapper.canvas` (a renderer this arm
    does not edit), and `01b` spells the same eleven glyphs."""
    from mapper import canvas

    wires = {ord(g) for g in canvas._GLYPH.values() if g.strip()}  # noqa: SLF001
    owned = {cp for lo, hi in darkside.DECLARED_GLYPH_RANGES["V29"] for cp in range(lo, hi + 1)}
    assert owned == wires, (sorted(map(chr, owned - wires)), sorted(map(chr, wires - owned)))
    assert ord("╳") not in owned and ord("╱") not in owned


def test_amendment_2a_the_D7_row_contributes_no_member():
    assert "V18" in {r[0] for r in derived_rows()}, "V18 left 01b; this arm lost its subject"
    assert "V18" not in {m[0] for m in darkside.DECLARED_VOCABULARY}


def test_hlr_n16_2_each_view_paints_the_rows_its_01b_views_column_names():
    """The per-view partition, derived from `01b`'s Views column, not listed.

    Verdict `D3`: radial and outline have vocabularies of their own, and
    braille belongs to radial alone.  The view names are `darkside.VIEW_NAMES`
    (English since the 2026-09-29 language ruling, assumption `A6`), and the
    `01b` Views column must spell exactly those.
    """
    views_of = _views_by_row()
    assert views_of.get("V21a"), "the suffixed rows fell out of the Views walk"
    declared_ids = {m[0] for m in darkside.DECLARED_VOCABULARY}
    want: dict[str, set[str]] = {}
    for vid in declared_ids:
        for view in views_of[vid]:
            want.setdefault(view, set()).add(vid)
    assert {v: set(ids) for v, ids in darkside.LEGEND_VIEWS.items()} == want
    assert set(want) == set(darkside.VIEW_NAMES.values()), set(want)
    radial, atlas = darkside.VIEW_NAMES["radial"], darkside.VIEW_NAMES["canvas"]
    assert "V4b" in want[radial] and "V4b" not in want[atlas]


def test_design_pass_a_retired_id_is_never_a_row_again():
    """Every id the change log retires is gone from the tables and from the
    declaration -- a retired id is never reused, so a trace that cites it
    cannot silently land on a different form."""
    retired = _retired_ids()
    assert {"V4", "V4a", "V5", "V6", "V7", "V8", "V9", "V10", "V17"} <= retired, retired
    rows = {r[0] for r in derived_rows()}
    declared = {m[0] for m in darkside.DECLARED_VOCABULARY}
    assert not retired & rows, retired & rows
    assert not retired & declared, retired & declared


def test_design_pass_q4_the_lens_rows_are_marked_deferred_and_not_declared():
    """Verdict `Q4`: `V11`-`V16` carry the `#D7` marker and leave the declaration."""
    lens = {f"V{n}" for n in range(11, 17)}
    marked = {r[0] for r in derived_rows() if "DEFERRED(#D7)" in "".join(r)}
    assert lens <= marked, lens - marked
    assert not lens & {m[0] for m in darkside.DECLARED_VOCABULARY}


def test_llr_n16_2_1_the_colour_rows_EQUAL_section_3_5():
    """The second derived set: `01b` §3.5's colours with a job, hex included."""
    text = UX.read_text(encoding="utf-8")
    table = text[text.index("### 3.5 "):text.index("### 3.6 ")]
    rows = re.findall(r"^\|\s*`(.)`\s*\|\s*`([^`]+)`\s*\|\s*\**`([A-Z]+)`\**\s*\|\s*`(#[0-9a-f]{6})`",
                      table, re.M)
    assert len(rows) >= 2, f"the colour table walk derived {rows}"
    assert list(darkside.DECLARED_COLOURS) == [(s, lab, tok) for s, lab, tok, _hex in rows]
    for _s, _lab, tok, hexv in rows:
        assert darkside.tokens()[tok] == hexv, (tok, hexv)


# ---------------------------------------------------------------------------
# `INC8-CR-F3` -- 01b §3.6, the legend's own framing copy, walked the same way
# §3.5's colour table is above: byte-read, UTF-8 decoded explicitly, anchored
# on literal text, failing loudly on a missing anchor, and compared in order.

_SECTION_36 = re.compile(r"### 3\.6 .*?(?=### 3\.7 )", re.S)
_HEADERS_LINE = re.compile(r"Section headers, in order:\s*(.+)")
_FOOTER_LINE = re.compile(r"Footer, two lines:\s*(.+)")
_BACKTICK_RUN = re.compile(r"`([^`]+)`")


def _section_36() -> str:
    text = UX.read_bytes().decode("utf-8")
    match = _SECTION_36.search(text)
    assert match, "01b's §3.6 (Legend framing copy) is missing -- nothing to derive from"
    return match.group(0)


def test_inc8_cr_f3_the_section_headers_and_footer_EQUAL_section_3_6():
    """01b §3.6 names the legend's section headers and footer VERBATIM.
    `help.SECTION_KEYS`/`SECTION_VOCABULARY`/`SECTION_COLOURS`/`FOOTER_LINES`
    were copied from it by hand and NOTHING derived them from the document --
    the same defect `test_llr_n16_2_1_the_declaration_is_not_a_second_opinion`
    exists to catch for the vocabulary table, unaddressed here until now.

    The headers are in PAINTED order, the vocabulary first (verdict `E1`).
    The own-scope group's title was un-ratified until verdict `E3`; it is
    asserted by `test_e3_the_title_hint_and_own_scope_copy_EQUAL_section_3_6`.
    """
    section = _section_36()

    headers_line = _HEADERS_LINE.search(section)
    assert headers_line, f"the section-headers line is not in 01b's §3.6: {section!r}"
    headers = tuple(_BACKTICK_RUN.findall(headers_line.group(1)))
    assert headers == (
        help_screen.SECTION_VOCABULARY, help_screen.SECTION_COLOURS, help_screen.SECTION_KEYS,
    ), headers

    footer_line = _FOOTER_LINE.search(section)
    assert footer_line, f"the footer line is not in 01b's §3.6: {section!r}"
    footer = tuple(_BACKTICK_RUN.findall(footer_line.group(1)))
    assert footer == help_screen.FOOTER_LINES, footer


_TITLE_LINE = re.compile(r"Panel title:\s*`([^`·]+?) · ")
_TOP_RIGHT_LINE = re.compile(r"Top-right:\s*`(\S+) (\S+)`")
_OWN_TITLE_LINE = re.compile(r"Own-scope group title:\s*`([^`]+)`")
_OWN_WORDS_LINE = re.compile(r"Own-scope group words, by action:\s*(.+)")
_OWN_WORD_ITEM = re.compile(r"`([^`]+)`\s*\(((?:`[^`]+`,?\s*)+)\)")


def test_e3_the_title_hint_and_own_scope_copy_EQUAL_section_3_6():
    """Verdict `E3` ratified the own-scope group and its title, and the
    language ruling put every legend string in English.  So the rest of §3.6
    is walked the same way as the headers above: the title's first word, the
    close hint, the group's title, and one word per `SCOPE_HELP` action --
    with its key glyphs, read from the seat -- in `01b`'s order.  Every action
    of the legend's own scope has a word, so no own key can go unpainted."""
    from mapper.keymap import SCOPE_HELP, bindings_for

    section = _section_36()
    title = _TITLE_LINE.search(section)
    assert title and title.group(1) == help_screen.LEGEND_TITLE, title
    top_right = _TOP_RIGHT_LINE.search(section)
    close = next(b for b in bindings_for(SCOPE_HELP) if b.action == "dismiss_none")
    assert top_right and top_right.groups() == (
        close.glyph, help_screen.own_scope_word(close.action)), top_right
    own_title = _OWN_TITLE_LINE.search(section)
    assert own_title and own_title.group(1) == help_screen.LEGEND_OWN_SCOPE_GROUP, own_title
    words_line = _OWN_WORDS_LINE.search(section)
    assert words_line, "the own-scope words line is not in 01b's §3.6"
    doc = [(word, tuple(_BACKTICK_RUN.findall(glyphs)))
           for word, glyphs in _OWN_WORD_ITEM.findall(words_line.group(1))]
    seat = bindings_for(SCOPE_HELP)
    painted = [(word, tuple(b.glyph for b in seat if b.action in actions))
               for actions, word in help_screen.OWN_SCOPE_COPY]
    assert doc == painted, (doc, painted)
    worded = {a for actions, _w in help_screen.OWN_SCOPE_COPY for a in actions}
    assert {b.action for b in seat} == worded, {b.action for b in seat} ^ worded


def test_llr_n16_2_1_the_declaration_is_not_a_second_opinion():
    """The docstring's own claim, made true: something reads both and compares.

    Asserted as a PROPERTY of this module rather than as prose in `darkside.py`,
    because prose is what the previous version had.
    """
    assert derived_rows(), "no derivation ran"
    assert darkside.DECLARED_VOCABULARY, "nothing is declared to check"
