"""The `structure:` block of `mapper --audit` (HLR-RMU.1, LLR-RMU.1.2-.1.4).

`structure_lines(repo)` is the one frozen name here (D5): it derives the canon map ONCE, ranks the
gaps once and returns the block's lines, the informational header first.  The lines are
repository-derived and UNESCAPED: the sink must escape them (`reqharness.audit.run_cli` does, with
the report's own escaper) and so must any other caller (a status strip, a log).

`format_structure` is the pure formatter and a tested seam (not frozen).  It performs the
120-character cut ITSELF, so a caller that bypasses `structure_lines` still gets cut values; no
line it returns is longer than 1,000 characters.  Everything a profile names (kinds, edge types,
severities) is printed in the profile's own order, never in set or dict-hash order, so the output is
byte-identical from run to run.

Nothing here is written, spawned or opened other than through `descriptor.read_repo_text` (via the
adapter and the descriptor loader).  A canon over the node or edge cap is one fixed line
(`LIMIT_LINE`, ledger .62); `reqharness.audit.run_cli` keeps `internal error: <Type>` as the
fallback for anything else.  `refusal_line` is defined beside the cause table in
`relmap.descriptor` (ledger .56) and imported here.
"""
from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from mapper.relmap.adapter import CanonUnavailable, derive_reqharness_map
from mapper.relmap.descriptor import (
    CANON_NAME,
    CAUSE,
    MAX_DESCRIPTORS,
    DescriptorError,
    default_descriptor,
    discover_descriptors,
    load_descriptor,
    refusal_line,
)
from mapper.relmap.gaps import Gap, detect_gaps, rank_gaps
from mapper.relmap.model import RelMap, RelMapLimitError, cut
from mapper.relmap.profile import SEVERITIES

HEADER = "structure: informational - does not change the verdict or the exit code"
LIMIT_LINE = "structure: unavailable (canon: over the node or edge limit)"
DESCRIPTOR_OVERFLOW = f"structure: refused: more descriptors than the limit ({MAX_DESCRIPTORS})"
MAX_GAP_LINES = 20
MAX_NOTE_LINES = 10
UNLINKED_SHOWN = 5
SENTENCE_MAX = 400
ROW_PREFIX = "unparsed row "
#: the builder's problem kinds, in the order the contract's table lists them
PROBLEM_KINDS = (
    "duplicate id", "unsafe id", "unknown node kind", "unknown edge type", "unknown endpoint", "disallowed pair",
)
_ELLIPSIS = "…"
_DOT = " · "


def _cause_text(cause: str, limit: int) -> str:
    return f"exceeds the {limit} byte limit" if cause == CAUSE["K5"] else cause


def _sentence(text: str) -> str:
    return text if len(text) <= SENTENCE_MAX else text[: SENTENCE_MAX - 1] + _ELLIPSIS


def _summary(m: RelMap) -> str:
    profile = m.profile
    kinds = {k: 0 for k in profile.node_kinds}
    for node in m.nodes:
        kinds[node.kind] = kinds.get(node.kind, 0) + 1
    types = {t.name: 0 for t in profile.edge_types}
    for edge in m.edges:
        types[edge.type] = types.get(edge.type, 0) + 1

    def part(total: int, counts: dict[str, int]) -> str:
        inner = ", ".join(f"{name}={n}" for name, n in counts.items() if n)
        return f"{total} ({inner})" if inner else str(total)

    return (
        f"structure: profile={profile.name} nodes={part(len(m.nodes), kinds)} "
        f"edges={part(len(m.edges), types)} cycles={len(m.cycles)}"
    )


def _skipped(m: RelMap, unknown_status: int, reach_not_computed: int) -> str | None:
    counts: dict[str, int] = {}
    for problem in m.problems:
        counts[problem.kind] = counts.get(problem.kind, 0) + 1
    ordered = [k for k in PROBLEM_KINDS if k in counts] + sorted(k for k in counts if k not in PROBLEM_KINDS)
    parts = []
    if m.problems:
        inner = ", ".join(f"{k}={counts[k]}" for k in ordered)
        parts.append(f"skipped {len(m.problems)} canon rows ({inner})")
    if unknown_status:
        parts.append(f"unknown status={unknown_status}")
    if reach_not_computed:
        parts.append(f"reach not computed={reach_not_computed}")
    return "structure: " + "; ".join(parts) if parts else None


def _note_texts(
    notes: Sequence[str], unlinked: Sequence[str], ignored: Sequence[str]
) -> list[str]:
    """The note texts in the stated order, every repository-derived value cut to 120."""
    out = []
    for note in notes:
        if note.startswith(ROW_PREFIX):
            out.append(ROW_PREFIX + cut(note[len(ROW_PREFIX):]))
        else:
            out.append(cut(note))
    if unlinked:
        shown = ", ".join(cut(i) for i in unlinked[:UNLINKED_SHOWN])
        more = f" and {len(unlinked) - UNLINKED_SHOWN} more" if len(unlinked) > UNLINKED_SHOWN else ""
        out.append(f"unlinked LLRs ({len(unlinked)}): {shown}{more}")
    for key in ignored:
        out.append(f"ignored descriptor key: {cut(key)}")
    return out


def format_structure(
    relmap: RelMap,
    gaps: Sequence[Gap],
    notes: Sequence[str],
    refusals: Sequence[str],
    *,
    label: str | None,
    sources: tuple[str | None, str | None] = (None, None),
    unknown_status: int = 0,
    reach_not_computed: int = 0,
    unlinked: Sequence[str] = (),
    ignored: Sequence[str] = (),
) -> list[str]:
    """One descriptor's block (or, when `refusals` is not empty, exactly those lines).

    `gaps` is the RANKED list of every gap; at most 20 print, the rest are counted.  `notes` are
    the adapter's printed notes (`Derivation.reported`); `unlinked` the ids of the LLRs that
    resolved to no HLR; `ignored` the descriptor's ignored keys; `label` the descriptor's base name
    (`None`: the built-in default).  Every value printed is cut to 120 characters here, before the
    sink escapes it.
    """
    if refusals:
        return list(refusals)
    lines = [f"structure: descriptor {cut(label) if label is not None else '(built-in default)'}"]
    lines.append(_summary(relmap))
    us_canon, at_table = (cut(v) if v is not None else "unset" for v in sources)
    lines.append(f"structure: sources: canon={CANON_NAME} us_canon={us_canon} at_table={at_table}")
    by_severity = {s: 0 for s in SEVERITIES}
    for gap in gaps:
        by_severity[gap.severity] = by_severity.get(gap.severity, 0) + 1
    lines.append(
        f"structure: gaps: {len(gaps)} (" + ", ".join(f"{s}={by_severity[s]}" for s in SEVERITIES) + ")"
    )
    for gap in gaps[:MAX_GAP_LINES]:
        lines.append(
            f"structure gap: {gap.severity}{_DOT}{gap.kind}{_DOT}{cut(gap.node)}{_DOT}"
            f"reach={gap.reach}{_DOT}{_sentence(gap.sentence)}"
        )
    if len(gaps) > MAX_GAP_LINES:
        lines.append(
            f"structure: gaps shown {MAX_GAP_LINES} of {len(gaps)} ({len(gaps) - MAX_GAP_LINES} lowest-ranked not shown)"
        )
    skipped = _skipped(relmap, unknown_status, reach_not_computed)
    if skipped is not None:
        lines.append(skipped)
    texts = _note_texts(notes, unlinked, ignored)
    for text in texts[:MAX_NOTE_LINES]:
        lines.append(f"structure note: {text}")
    if len(texts) > MAX_NOTE_LINES:
        lines.append(
            f"structure: notes shown {MAX_NOTE_LINES} of {len(texts)} ({len(texts) - MAX_NOTE_LINES} not shown)"
        )
    return lines


def structure_lines(repo: Path) -> list[str]:
    """The block for `repo`: the informational header, then one block or refusal line per
    descriptor in code-point order of its base name (the built-in default when there is none), then
    the descriptor overflow line.  The canon map is derived and ranked ONCE per call.  The returned
    lines are UNESCAPED: the caller's sink must escape them."""
    lines = [HEADER]
    paths, overflow = discover_descriptors(repo)
    try:
        derivation = derive_reqharness_map(repo, default_descriptor())
    except CanonUnavailable as exc:
        return lines + [f"structure: unavailable (canon: {_cause_text(exc.cause, exc.limit)})"]
    except RelMapLimitError:
        return lines + [LIMIT_LINE]
    ranked, not_computed = rank_gaps(derivation.map, detect_gaps(derivation.map), MAX_GAP_LINES)
    for path in paths or (None,):
        if path is None:
            name, descriptor = None, default_descriptor()
        else:
            name = path.name
            try:
                descriptor = load_descriptor(path, repo)
            except DescriptorError as exc:
                refusal = refusal_line(exc.name, exc.cause, exc.limit)
                lines += format_structure(derivation.map, ranked, (), (refusal,), label=name)
                continue
        lines += format_structure(
            derivation.map, ranked, derivation.reported, (), label=name,
            sources=(descriptor.us_canon, descriptor.at_table),
            unknown_status=derivation.unknown_status, reach_not_computed=not_computed,
            unlinked=derivation.unlinked, ignored=descriptor.ignored_keys,
        )
    if overflow:
        lines.append(DESCRIPTOR_OVERFLOW)
    return lines


__all__ = [
    "HEADER", "LIMIT_LINE", "format_structure", "refusal_line", "structure_lines",
]
