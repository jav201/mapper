"""Canvas audit hook — LLR-Q3.2.1 / LLR-Q3.2.2 (batch 2026-10-23-hygiene-batch, lane L3).

Pre-state, executed at the L3 RED gate: `Canvas.__init__` declared no `audit`
parameter and `put` recorded nothing — every arm below failed on the
constructor call itself.  Event set v1 = clip + overprint (orchestrator ruling
R4, ledger `LED-2026-10-23-hygiene-batch.4`): a clip is an out-of-bounds write
of a non-space character; an overprint is an in-bounds write whose cell already
holds a DIFFERENT alphanumeric character and whose own written character is
also alphanumeric (the second limb names mutant M-Q3-4, ledger `.10`).
Asserting mutants: M-Q3-2 (event append removed) · M-Q3-3 (sink touches the
cell write) · M-Q3-4 (alphanumeric gate dropped).
"""
from mapper.canvas import Canvas

_UD = 1 | 2


def test_events():
    """LLR-Q3.2.1 — clip/overprint coordinates recorded; every other write silent."""
    audit = {"clip": [], "overprint": []}
    cv = Canvas(4, 2, audit=audit)
    cv.put(4, 0, "X")            # out of bounds, non-space  -> clip
    cv.put(-1, 1, "Y")           # out of bounds, non-space  -> clip
    cv.put(4, 1, " ")            # out of bounds space       -> nothing
    cv.put(0, 0, " ")            # in-bounds space write     -> nothing
    cv.put(0, 0, "A")
    cv.put(0, 0, "A")            # same character            -> not an overprint
    cv.put(0, 0, "B")            # different alphanumeric    -> overprint
    cv.put(1, 0, "│")            # box drawing, not alnum    -> nothing
    cv.put(1, 0, "─")
    cv.put(2, 0, "C")
    cv.put(2, 0, "│")            # held alnum, NEW not alnum -> nothing (M-Q3-4)
    cv.put(3, 0, "3")
    cv.put(3, 0, "7")            # digits are alphanumeric   -> overprint
    assert audit["clip"] == [(4, 0), (-1, 1)]
    assert audit["overprint"] == [(0, 0), (3, 0)]


def test_text_and_wire_paths_share_put_and_default_sink_is_none():
    """`text` loops through `put` and inherits the audit; no sink, no crash."""
    cv = Canvas(6, 2)
    cv.put(9, 9, "X")            # no sink at all: silently dropped, no event
    audit = {}
    watched = Canvas(6, 2, audit=audit)
    watched.text(5, 0, "AB")     # 'A' at x=5 ok, 'B' at x=6 clips
    assert audit == {"clip": [(6, 0)]}


def _write_sequence(audit) -> Canvas:
    """One fixed write sequence — cells, wires, edges, overprint and a clip."""
    cv = Canvas(10, 4, audit=audit)
    cv.text(0, 0, "root")
    cv.put(6, 0, "X")
    cv.put(6, 0, "Y")            # overprint under the sink
    cv.wire(1, 1, _UD)
    cv.edge(1, 0, 1, 3)
    cv.elbow_down(0, 1, 9, 3)
    cv.put(12, 0, "Q")           # clipped
    cv.put(2, 0, " ")            # space overwrite of a held letter: no event
    return cv


def test_byte_identity():
    """LLR-Q3.2.2 — `rows()` identical (plain and spans) with vs. without the sink."""
    rows_plain = _write_sequence(None).rows()
    sink = {"clip": [], "overprint": []}
    rows_audited = _write_sequence(sink).rows()
    assert [r.plain for r in rows_plain] == [r.plain for r in rows_audited]
    spans_plain = [
        [(s.start, s.end, str(s.style)) for s in row.spans] for row in rows_plain
    ]
    spans_audited = [
        [(s.start, s.end, str(s.style)) for s in row.spans] for row in rows_audited
    ]
    assert spans_plain == spans_audited
    assert sink["overprint"] == [(6, 0)]
    assert sink["clip"] == [(12, 0)]
