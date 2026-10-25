"""The `reqharness` canon adapter: `REQUIREMENTS.md` -> `RelMap`, derived read-only (HLR-RMA.1).

The canon carries no parent column, so the HLR -> LLR `refines` edge comes from id structure
alone (rule D-1): drop the last dot-separated segment of an LLR id, prefix `HLR-`, and link only
when that id is an HLR node.  An LLR that does not resolve is LISTED (`Derivation.unlinked`),
never attached to a nearest guess.  A row `parse_canon` could not read is LISTED
(`Derivation.reported`), never re-parsed.  Both lists qualify the HLRs near them
(`Node.unparsed`), so a gap sentence can say the canon was not fully readable there.

Only HLR and LLR are sourced: the canon does not hold US, AT or TC rows, so those kinds are
absent from `RelMap.sourced` and every gap row that needs one stays silent (MAP-TYPES 6.1).

The canon is read once, through `read_repo_text` (lstat, link and non-regular refusal, capped
read) and parsed once with `reqharness.derive.parse_canon`; nothing else is opened, written or
spawned.  `us_canon` / `at_table` of a descriptor are never opened here (they are surfaced as
"configured, not derivable in R1" by the audit's sources line).

`Derivation.reported` holds the PRINTED note text, repository-derived and UNCUT: the formatter
cuts and escapes it.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, replace
from pathlib import Path

from mapper.relmap.descriptor import Descriptor, RepoReadError, read_repo_text
from mapper.relmap.model import Edge, Node, RelMap, build_map, cut
from mapper.relmap.profile import REQHARNESS
from mapper.reqharness.derive import LIMIT_ROLES_YML_BYTES, parse_canon

SOURCED = ("HLR", "LLR")
STATUS_WORDS = frozenset({"active", "deferred", "superseded", "withdrawn", "split"})
NOTE_UNPARSED_ROW = "unparsed row {id}"
NOTE_UNPARSED_LINE = "unparsed canon line"

# `parse_canon` words a row it cannot read as `... cannot parse row for {id!r} (n cells, expected m)`;
# the id is a Python repr, so it is read back with `ast.literal_eval`, never by hand.
_REPORT_ID = re.compile(r"cannot parse row for ('(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\") \(\d+ cells, expected \d+\)$")


class CanonUnavailable(Exception):
    """The canon could not be read.  `cause` is the fixed text of K1-K7, `limit` the byte cap."""

    def __init__(self, cause: str, limit: int) -> None:
        super().__init__(cause)
        self.cause = cause
        self.limit = limit


@dataclass(frozen=True)
class Derivation:
    """The map and its derivation notes.

    `reported`: one printed note per row `parse_canon` could not read, in canon order
    (`unparsed row <id>`, or `unparsed canon line` when the report names no id).
    `unlinked`: the ids of the LLR nodes that resolved to no HLR, in canon order.
    `unknown_status`: nodes whose status word is outside the known set (ineligible, kept).
    """

    map: RelMap
    reported: tuple[str, ...]
    unlinked: tuple[str, ...]
    unknown_status: int


def _report_id(report: str) -> str | None:
    match = _REPORT_ID.search(report)
    if match is None:
        return None
    try:
        value = ast.literal_eval(match.group(1))
    except (ValueError, SyntaxError):
        return None
    return value if isinstance(value, str) else None


def _status_word(cell: str) -> str:
    words = cell.split()
    return words[0].lower() if words else ""


def _candidate(llr_id: str) -> str | None:
    """Rule D-1: the HLR id an LLR id points at, or None for an id with no dot."""
    tail = llr_id[len("LLR-"):]
    if "." not in tail:
        return None
    return "HLR-" + tail.rsplit(".", 1)[0]


def _unparsed_counts(hlrs: list[str], orphans: list[str]) -> dict[str, int]:
    """HLR id -> how many orphan LLR ids sit near it (LLR-RMA.1.3).

    `LLR-<t>` is near `HLR-<s>` when `<t>` starts with `<s>.`, or when `<s>` has a dot and the
    orphan's rule-D-1 stem equals `<s>` minus its last segment.  The two tests are disjoint
    (the stem of a longer id never equals the shorter one's parent), so one pass counts both.
    """
    under: dict[str, int] = {}
    sibling: dict[str, int] = {}
    for orphan in orphans:
        tail = orphan[len("LLR-"):]
        for i, ch in enumerate(tail):
            if ch == ".":
                prefix = tail[:i]
                under[prefix] = under.get(prefix, 0) + 1
        if "." in tail:
            stem = tail.rsplit(".", 1)[0]
            sibling[stem] = sibling.get(stem, 0) + 1
    counts: dict[str, int] = {}
    for hlr in hlrs:
        s = hlr[len("HLR-"):]
        n = under.get(s, 0)
        if "." in s:
            n += sibling.get(s.rsplit(".", 1)[0], 0)
        if n:
            counts[hlr] = n
    return counts


def derive_reqharness_map(repo: Path, descriptor: Descriptor) -> Derivation:
    """The `reqharness` relation map of `repo`, derived read-only from its canon.

    Raises `CanonUnavailable` (K1-K7) when the canon cannot be read; a canon with no HLR/LLR row
    yields an empty map.  `build_map` may raise `RelMapLimitError` for a canon over the node or
    edge cap; the caller treats that as a failure of the derivation, not of the canon read.
    """
    try:
        text = read_repo_text(Path(repo) / descriptor.canon, LIMIT_ROLES_YML_BYTES)
    except RepoReadError as exc:
        raise CanonUnavailable(exc.cause, exc.limit) from None
    objects, reports = parse_canon(text)

    nodes = tuple(
        Node(
            o.id,
            o.class_id,
            cut(o.fields.get("statement", "")),
            _status_word(o.fields.get("status", "")),
        )
        for o in objects
    )
    # First pass: which nodes the builder keeps (a duplicate or unsafe id is excluded there),
    # so an edge is only ever drawn between nodes that exist.
    kept = build_map(REQHARNESS, nodes, (), sourced=SOURCED).nodes
    hlr_ids = {n.id for n in kept if n.kind == "HLR"}

    edges: list[Edge] = []
    unlinked: list[str] = []
    for n in kept:
        if n.kind != "LLR":
            continue
        parent = _candidate(n.id)
        if parent in hlr_ids:
            edges.append(Edge(parent, n.id, "refines"))
        else:
            unlinked.append(n.id)

    notes: list[str] = []
    orphans = list(unlinked)
    for report in reports:
        row_id = _report_id(report)
        if row_id is None:
            notes.append(NOTE_UNPARSED_LINE)
            continue
        notes.append(NOTE_UNPARSED_ROW.format(id=row_id))
        if row_id.startswith("LLR-"):
            orphans.append(row_id)
    counts = _unparsed_counts([n.id for n in kept if n.kind == "HLR"], orphans)

    final = build_map(
        REQHARNESS,
        tuple(replace(n, unparsed=counts.get(n.id, 0)) if n.kind == "HLR" else n for n in nodes),
        edges,
        sourced=SOURCED,
    )
    unknown = sum(1 for n in final.nodes if n.status not in STATUS_WORDS)
    return Derivation(final, tuple(notes), tuple(unlinked), unknown)
