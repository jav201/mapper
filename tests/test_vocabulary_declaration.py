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

    FAITHFULNESS, NOT SET EQUALITY. Set equality needs the compound-row
    projection AND the glyph-set model applied to every row; this arm asserts the
    weaker, decisive property that every row the product declares actually
    appears in `01b` with that style. **Fabrication is what it catches**, and
    fabrication is what happened.
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


def test_llr_n16_2_1_the_declaration_is_not_a_second_opinion():
    """The docstring's own claim, made true: something reads both and compares.

    Asserted as a PROPERTY of this module rather than as prose in `darkside.py`,
    because prose is what the previous version had.
    """
    assert derived_rows(), "no derivation ran"
    assert darkside.DECLARED_VOCABULARY, "nothing is declared to check"
