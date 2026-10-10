"""B-105 / AT-063 of `2026-10-09-canon-batch`.

The fold keeps an existing id and never rewrites it, so `2026-10-09-hygiene-batch`
— which reused `HLR-001`…`LLR-002.1` — never reached the canon while `V22` read
green.  Its five rows were appended by hand under `HYG` ids, each naming the id
its record uses, and this test pins that fold-down: the canon row's statement
must equal the record's statement under the fold's normalisation, plus the
`(Record id: …)` suffix, owned by the hygiene batch and `active`.

The normalisation is pinned here as literals (not imported from the fold), so a
drift of either side goes RED.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANON = ROOT / "REQUIREMENTS.md"
HYGIENE_RECORD = ROOT / ".dev-flow" / "2026-10-09-hygiene-batch" / "01-requirements.md"

ALIAS = {
    "HLR-001": "HLR-HYG.1",
    "HLR-002": "HLR-HYG.2",
    "LLR-001.1": "LLR-HYG.1.1",
    "LLR-001.2": "LLR-HYG.1.2",
    "LLR-002.1": "LLR-HYG.2.1",
}

_HEADING_RE = re.compile(r"^###\s+((?:HLR|LLR)-\d{3}(?:\.\d+)?)\s+—\s")
_STATEMENT_PREFIX = "- **Statement:** "


def _canon_rows() -> list[tuple[str, list[str]]]:
    """The requirement table as a list of (first_cell, cells).

    Anchored on the `| Id |` header line, read until the first non-row line.
    `first_cell` is the id (`split("|")[1]`, as the fold reads it); `cells` is
    the row split on UNESCAPED pipes only, so `str \\| None` stays inside the
    statement cell.
    """
    rows: list[tuple[str, list[str]]] = []
    in_table = False
    for line in CANON.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Id |"):
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("|---"):
            continue
        if not line.startswith("|"):
            break
        first_cell = line.split("|")[1].strip()
        cells = re.split(r"(?<!\\)\|", line)
        rows.append((first_cell, cells))
    return rows


def _normalise(text: str) -> str:
    """The fold's four rules, as literals (LLR-CAN.1.1)."""
    text = text.replace("`", "")
    text = text.replace("**", "")
    text = text.strip(" \t*-")
    text = re.sub(r"\s*\*\([^*]*\)$", "", text)
    text = text.replace("|", "\\|")
    return text


def _record_statements() -> dict[str, str]:
    """record id -> raw statement, parsed from the hygiene record's headings."""
    statements: dict[str, str] = {}
    headings: list[str] = []
    current: str | None = None
    for line in HYGIENE_RECORD.read_text(encoding="utf-8").splitlines():
        match = _HEADING_RE.match(line)
        if match:
            current = match.group(1)
            headings.append(current)
            continue
        if current is not None and line.startswith(_STATEMENT_PREFIX):
            statements[current] = line[len(_STATEMENT_PREFIX):]
            current = None
    # CR-1: a repeated heading would collapse in the dict; count the headings themselves.
    assert len(headings) == 5 and len(set(headings)) == 5, f"record headings: {headings}"
    return statements


def test_at_063_every_hygiene_requirement_is_in_the_canon_once():
    """AT-063 (HLR-CAN.1 / LLR-CAN.1.1): each hygiene heading folds into exactly
    one canon row under its HYG id, whose statement equals the record's statement
    under the fold's normalisation plus the `(Record id: …)` suffix, owned by the
    hygiene batch and `active`."""
    record = _record_statements()
    assert set(record) == set(ALIAS), (
        f"record ids {sorted(record)} != {sorted(ALIAS)}"
    )
    rows = _canon_rows()
    for record_id, canon_id in ALIAS.items():
        raw = record[record_id]
        expected = _normalise(raw) + f" (Record id: {record_id}.)"
        matches = [cells for first_cell, cells in rows if first_cell == canon_id]
        assert len(matches) == 1, (
            f"{record_id}: expected exactly one canon row for {canon_id}, "
            f"found {len(matches)}"
        )
        cells = matches[0]
        statement = cells[2].strip()
        owner = cells[3].strip()
        status = cells[4].strip()
        assert statement == expected, (
            f"{record_id}: statement drifted from its record"
        )
        assert owner == "2026-10-09-hygiene-batch", (
            f"{record_id}: owner {owner!r} != '2026-10-09-hygiene-batch'"
        )
        assert status == "active", f"{record_id}: status {status!r} != 'active'"


def test_llr_can_1_2_canon_ids_are_unique_and_the_table_is_not_empty():
    """LLR-CAN.1.2: no canon id appears twice, and the table holds at least 134
    rows (129 before this batch + 5 appended)."""
    rows = _canon_rows()
    assert len(rows) >= 134, f"expected at least 134 canon rows, found {len(rows)}"
    seen: dict[str, int] = {}
    for first_cell, _cells in rows:
        seen[first_cell] = seen.get(first_cell, 0) + 1
    duplicates = sorted(cid for cid, count in seen.items() if count > 1)
    assert not duplicates, f"duplicate canon ids: {duplicates}"


def test_llr_can_1_1_normaliser_pins_the_fold_rules():
    """LLR-CAN.1.1: the normaliser's four rules, as literal arms, so a drift of
    the fold or of this test goes RED."""
    assert _normalise("`a` **b**") == "a b"
    assert _normalise("x | y") == "x \\| y"
    assert _normalise("text *(note)*") == "text"
    assert _normalise("- `str | None` -") == "str \\| None"
