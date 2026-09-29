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
    assert "V4a" in ids and "V4b" in ids, (
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
_QUALIFIER = re.compile(r"([a-z]+)\s")
_STYLE_TOKEN = re.compile(r"`((?:bold\s+)?[A-Z][A-Z_]*(?:\s+on\s+[A-Z][A-Z_]*)?)`")

#: Rows whose glyph cell is PROSE: the rule derives no sample, the declaration
#: carries `""`, and each is an open question for the operator
#: (`increment-022` §Questions).  Pinned so a cell that gains a glyph, or a
#: glyph that goes missing, reddens instead of passing.
OPERATOR_QUESTIONS = {"V4b", "V12"}

#: `HLR-N16.2`'s view partition, by `01b` section.  `3.1` names its view
#: ("the atlas view") and `3.4` its screen ("Sala (home)"); `3.2`'s minimap and
#: overflow indicators live on the same map canvas, which is an ASSUMPTION
#: recorded in `increment-022`.  `3.3` is the lens, deferred whole (`#D23`).
SECTION_VIEW = {"3.1": "atlas", "3.2": "atlas", "3.4": "sala"}


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
        that token, for every style of the row.  (`V17`, `V20`)
    G2  QUALIFIED PAIRS.  The style cell has several `;`-separated segments,
        each opening with a qualifier word, and the glyph cell pairs a token
        with each of those words (`` `█` filled ``): each style takes the token
        of the qualifier its segment opens with.  (`V19`)
    G3  LEADING RUN.  The backtick tokens opening the cell, whitespace-separated,
        joined with one space; a token with a `<placeholder>` is a TEMPLATE and
        is dropped, and if nothing remains the `e.g.` token stands in.  Prose
        after the run (a parenthetical, "rectangle inside ...") is a GLOSS, not
        glyph.  (`V3` -> `▸ inv +23`, `V10` -> `▓ ▒ ░`)
    G4  NOTHING.  A cell with no token is prose: `None`, and an operator
        question -- never a guess.  (`V4b`, `V12`)

    Codepoint RANGES (`` `U+2800`–`U+28FF` ``) are read separately by `_RANGE`;
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


def _rows_by_section() -> dict[str, str]:
    """Row id -> the `01b` section (`3.1`..`3.4`) its table sits in."""
    out: dict[str, str] = {}
    for number, body in re.findall(r"^### (3\.[1-4]) (.*?)(?=^### )", _section() + "### ",
                                   re.M | re.S):
        for row in ROW.findall(body):
            out[row[0]] = number
    return out


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


def test_amendment_2b_V4a_collapses_into_V4_carrying_its_braille_range():
    """`01b` Amendment 2(b): one painted form, a glyph SET with a range."""
    _, ranges = derived_members()
    declared_ids = {m[0] for m in darkside.DECLARED_VOCABULARY}
    assert "V4a" not in declared_ids and "V4" in declared_ids
    assert {k: set(v) for k, v in darkside.DECLARED_GLYPH_RANGES.items()} == ranges
    assert (0x2800, 0x28FF) in ranges["V4"], ranges


def test_amendment_2a_the_D7_row_contributes_no_member():
    assert "V18" in {r[0] for r in derived_rows()}, "V18 left 01b; this arm lost its subject"
    assert "V18" not in {m[0] for m in darkside.DECLARED_VOCABULARY}


def test_hlr_n16_2_each_view_paints_the_rows_of_its_own_01b_sections():
    """The per-view partition, derived from the sections rather than listed."""
    section_of = _rows_by_section()
    assert section_of.get("V4b") == "3.1", "the suffixed rows fell out of the section walk"
    declared_ids = {m[0] for m in darkside.DECLARED_VOCABULARY}
    want: dict[str, set[str]] = {}
    for vid in declared_ids:
        view = SECTION_VIEW.get(section_of[vid])
        if view:
            want.setdefault(view, set()).add(vid)
    assert {v: set(ids) for v, ids in darkside.LEGEND_VIEWS.items()} == want


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

    `help.LEGEND_OWN_SCOPE_GROUP` (`en esta leyenda`, `INC8-CR-F1`) is
    DELIBERATELY NOT asserted here: 01b §3.6 does not name it, and it stays an
    un-ratified Inc-8 constant (see the corrective-pass record) rather than a
    fourth row silently added to this equality.
    """
    section = _section_36()

    headers_line = _HEADERS_LINE.search(section)
    assert headers_line, f"the section-headers line is not in 01b's §3.6: {section!r}"
    headers = tuple(_BACKTICK_RUN.findall(headers_line.group(1)))
    assert headers == (
        help_screen.SECTION_KEYS, help_screen.SECTION_VOCABULARY, help_screen.SECTION_COLOURS,
    ), headers

    footer_line = _FOOTER_LINE.search(section)
    assert footer_line, f"the footer line is not in 01b's §3.6: {section!r}"
    footer = tuple(_BACKTICK_RUN.findall(footer_line.group(1)))
    assert footer == help_screen.FOOTER_LINES, footer


def test_llr_n16_2_1_the_declaration_is_not_a_second_opinion():
    """The docstring's own claim, made true: something reads both and compares.

    Asserted as a PROPERTY of this module rather than as prose in `darkside.py`,
    because prose is what the previous version had.
    """
    assert derived_rows(), "no derivation ran"
    assert darkside.DECLARED_VOCABULARY, "nothing is declared to check"
