"""HLR-RMU.1 / LLR-RMU.1.1-.1.4 -- the `structure:` block of `mapper --audit`, plus the Layer B
acceptance nodes of the whole relation-map batch (AT-117 ... AT-129) and the Layer A pins TC-RM-02
and TC-RM-03.

Two layers, named as such:

* Layer B: every `test_at_NNN_*` runs the REAL console entry (`mapper --audit <repo>`) in a
  subprocess with the 60 s timeout, over tmp repos built by `tests/_relmap_fixtures.py` (which
  IMPORTS the release-test builders).  The child is pinned to THIS checkout through PYTHONPATH and
  `test_child_runs_this_checkout` asserts it.  No elapsed-time assertion anywhere.
* Layer A: `format_structure` / `structure_lines` / `run_cli(argv, extra_lines=...)` in-process,
  where the surface cannot be reached from the shipped CLI (a raising callable, the `--baseline`
  refusal path, a 5,000-line generator, a 1 MiB value passed straight to the formatter).

The verdict is found by its PREFIX `verdict: ` (it is no longer the last line); the block is every
line after it.  Gap rows are for reading, not parsing.
"""
from __future__ import annotations

import dataclasses
import io
import os
import re
import sys
from pathlib import Path

import pytest

import mapper
from mapper.osopen import MAX_MAP_BYTES
from mapper.relmap import adapter as adapter_mod
from mapper.relmap import audit as raudit
from mapper.relmap.audit import HEADER, format_structure, structure_lines
from mapper.relmap.descriptor import CAUSE
from mapper.relmap.text import refusal_line
from mapper.relmap.gaps import Gap, detect_gaps, rank_gaps
from mapper.relmap.model import build_map
from mapper.relmap.profile import REQHARNESS
from mapper.reqharness import audit as audit_mod
from mapper.reqharness import identity
from mapper.reqharness.derive import LIMIT_ROLES_YML_BYTES, parse_canon
from mapper.reqharness.audit import _visible
from tests._relmap_fixtures import (
    CANON_HEADER,
    HLR_FIELDS,
    ONE_ROW,
    ROOT,
    _audit_cli,
    _git_repo,
    block_of,
    child_mapper_file,
    ready_repo,
    registry_repo,
    report_of,
    row,
    run_audit,
    run_audit_nohook,
)
from tests.test_relmap_descriptor import _make_link, _nested_flow, _padded

SNAPSHOT = ROOT / "tests" / "fixtures" / "relmap" / "REQUIREMENTS.snapshot.md"
DOT = " \u00b7 "
INFO = "structure: informational - does not change the verdict or the exit code"
SNAPSHOT_SUMMARY = "structure: profile=reqharness nodes=275 (HLR=76, LLR=199) edges=196 (refines=196) cycles=0"
SNAPSHOT_NOTE_IDS = (
    "LLR-HYG.1.1", "LLR-CAN.1.1", "LLR-CAN.1.2", "HLR-RH.6", "LLR-RH.6.1", "LLR-RH.7.3", "LLR-Q3.1.2",
)

# Captured by RUNNING `mapper --audit` on the base commit ab412fc (no hook yet) over the exit-0
# fixture `ready_repo(ONE_ROW)`, repository path replaced by `<repo>` (capture command and base SHA
# in the Inc-5 packet).  A line that moves fails AT-120.
GOLDEN_PREFIX = [
    "repo: <repo>",
    "chain: chain verified",
    "counts: reviewed=1, changed \u00b7 review=0, pre-reviewed=0, not reviewed=0, retired=0",
    "pre-reviews: 0",
    "unentitled reviews: 0",
    "identity: identity ceiling: git identity is self-claimed and spoofable by any committer; "
    "the chain proves integrity and approval, not authorship (LLR-RH.4.4)",
    "verdict: ready",
]


def _text(*rows: str) -> str:
    return CANON_HEADER + "".join(rows)


def _write(directory: Path, name: str, data: str | bytes) -> Path:
    path = directory / name
    path.write_bytes(data.encode("utf-8") if isinstance(data, str) else data)
    return path


def _gap_lines(block: list[str]) -> list[str]:
    return [line for line in block if line.startswith("structure gap: ")]


def _note_lines(block: list[str]) -> list[str]:
    return [line for line in block if line.startswith("structure note: ")]


def _by_prefix(block: list[str], prefix: str) -> list[str]:
    return [line for line in block if line.startswith(prefix)]


def _small_map(*nodes, edges=()):
    return build_map(REQHARNESS, tuple(nodes), tuple(edges), sourced=REQHARNESS.node_kinds)


def _node(node_id, kind="HLR", title="t", status="active", **kw):
    from mapper.relmap.model import Node

    return Node(node_id, kind, title, status, **kw)


def _edge(src, dst, type_="refines"):
    from mapper.relmap.model import Edge

    return Edge(src, dst, type_)


def _format(m, **kw):
    """`format_structure` over the detected, ranked gaps of `m`."""
    ranked, not_computed = rank_gaps(m, detect_gaps(m), 20)
    kw.setdefault("label", "x.relmap.yml")
    kw.setdefault("reach_not_computed", not_computed)
    return format_structure(m, ranked, kw.pop("notes", ()), kw.pop("refusals", ()), **kw)


# ----------------------------------------------------------------------- module-scoped runs


@pytest.fixture(scope="module")
def snapshot_repo(tmp_path_factory):
    return registry_repo(tmp_path_factory.mktemp("snap"), "snapshot", SNAPSHOT.read_bytes())


@pytest.fixture(scope="module")
def snapshot_run(snapshot_repo):
    proc = run_audit(str(snapshot_repo))
    assert proc.returncode == 1, proc.stderr  # unreviewed objects remain: the verdict is not ready
    assert "Traceback" not in proc.stderr
    return proc


@pytest.fixture(scope="module")
def hostile_run(tmp_path_factory):
    """Five hostile surfaces (plus ESC in a descriptor key) in ONE repo, ONE run (the arms below)."""
    canon = _text(
        row("HLR-A\u0301.1", "accent id statement", "active"),
        row("HLR-B\ufe0f.1", "emoji id statement", "active"),
        row("HLR-C.1", "bell \x1b[31mRED\x1b[0m and flip \u202eEVIL", "active"),
    )
    repo = registry_repo(tmp_path_factory.mktemp("hostile"), "hostile", canon)
    _write(repo, "e\u0301.relmap.yml", "{}\n")
    _write(repo, "forge.relmap.yml", '"\\u2028verdict: ready": 1\n')
    _write(repo, "esc.relmap.yml", '"\\x1b[31mred": 1\n')
    proc = run_audit(str(repo))
    assert proc.returncode == 1, proc.stderr
    return proc


# ----------------------------------------------------------------------- environment


def test_child_runs_this_checkout():
    """The subprocess ATs must exercise the worktree's `mapper`, not another checkout's."""
    here = Path(mapper.__file__).resolve()
    assert here.is_relative_to(ROOT)
    assert Path(child_mapper_file()).resolve() == here


def test_the_released_helper_is_the_same_entry(tmp_path):
    """The imported release-test runner and the relmap runner reach the same code (sanity)."""
    plain = tmp_path / "plain"
    plain.mkdir()
    a = _audit_cli("--audit", str(plain))
    b = run_audit(str(plain))
    assert (a.returncode, a.stdout) == (b.returncode, b.stdout)


# ----------------------------------------------------------------------- LLR-RMU.1.2 line formats


def test_line_formats():
    """The only evidence for the HIGH, LOW and reach-above-0 renderings of the kinds the canon
    cannot source: a synthetic multi-severity map (stated, not hidden)."""
    m = _small_map(
        _node("US-1", "US", "story"), _node("HLR-1", "HLR", "high"), _node("HLR-2", "HLR", "lonely"),
        _node("LLR-1", "LLR", "low"), _node("AT-1", "AT", "accept", open=True), _node("TC-1", "TC", "orphan"),
        edges=[_edge("US-1", "HLR-1"), _edge("HLR-1", "LLR-1")],
    )
    lines = _format(m, sources=("docs/us.md", None))
    assert lines[0] == "structure: descriptor x.relmap.yml"
    assert lines[1] == "structure: profile=reqharness nodes=6 (US=1, HLR=2, LLR=1, AT=1, TC=1) edges=2 (refines=2) cycles=0"
    assert lines[2] == "structure: sources: canon=REQUIREMENTS.md us_canon=docs/us.md at_table=unset"
    assert lines[3] == "structure: gaps: 5 (HIGH=2, MED=2, LOW=1)"
    assert _gap_lines(lines) == [
        "structure gap: HIGH" + DOT + "US WITHOUT AT" + DOT + "US-1" + DOT + "reach=2" + DOT + "US-1 has no covering AT: story",
        "structure gap: HIGH" + DOT + "OPEN AT WITHOUT TEST" + DOT + "AT-1" + DOT + "reach=0" + DOT + "AT-1 is open and bound to no test: accept",
        "structure gap: MED" + DOT + "LLR NOT VERIFIED" + DOT + "LLR-1" + DOT + "reach=0" + DOT + "LLR-1 has no verifying TC: low",
        "structure gap: MED" + DOT + "HLR WITHOUT LLR" + DOT + "HLR-2" + DOT + "reach=0" + DOT + "HLR-2 has no LLR under it: lonely",
        "structure gap: LOW" + DOT + "ORPHAN TC" + DOT + "TC-1" + DOT + "reach=0" + DOT + "TC-1 verifies nothing: orphan",
    ]
    assert not any(line.startswith("structure: skipped") for line in lines)  # all counts 0: omitted
    assert not _note_lines(lines)


def test_empty_map_prints_zero_totals_without_parentheses():
    lines = _format(_small_map())
    assert lines[1] == "structure: profile=reqharness nodes=0 edges=0 cycles=0"
    assert lines[3] == "structure: gaps: 0 (HIGH=0, MED=0, LOW=0)"
    assert len(lines) == 4


def test_label_default_and_named():
    m = _small_map()
    assert format_structure(m, [], (), (), label=None)[0] == "structure: descriptor (built-in default)"
    assert format_structure(m, [], (), (), label="a.relmap.yml")[0] == "structure: descriptor a.relmap.yml"


@pytest.mark.parametrize("count,shown_overflow", [(20, False), (21, True)])
def test_gap_cap_is_twenty_with_an_overflow_line(count, shown_overflow):
    m = _small_map(*[_node(f"HLR-G.{i}", "HLR", f"t{i}") for i in range(count)])
    lines = _format(m)
    assert len(_gap_lines(lines)) == 20
    assert lines[3] == f"structure: gaps: {count} (HIGH=0, MED={count}, LOW=0)"
    overflow = _by_prefix(lines, "structure: gaps shown")
    if shown_overflow:
        assert overflow == ["structure: gaps shown 20 of 21 (1 lowest-ranked not shown)"]
    else:
        assert overflow == []
    assert not any(line.startswith("structure gap: ") and "shown" in line for line in lines)


@pytest.mark.parametrize("count,shown_overflow", [(10, False), (11, True)])
def test_note_cap_is_ten_with_an_overflow_line(count, shown_overflow):
    notes = tuple(f"unparsed row LLR-N.{i}" for i in range(count))
    lines = _format(_small_map(), notes=notes)
    assert len(_note_lines(lines)) == 10
    overflow = _by_prefix(lines, "structure: notes shown")
    assert overflow == (["structure: notes shown 10 of 11 (1 not shown)"] if shown_overflow else [])


def test_notes_come_in_the_stated_order_and_the_unlinked_line_shows_five_ids():
    lines = _format(
        _small_map(), notes=("unparsed row LLR-R.1", "unparsed canon line"),
        unlinked=tuple(f"LLR-U.{i}" for i in range(8)), ignored=("extra_key",),
    )
    assert _note_lines(lines) == [
        "structure note: unparsed row LLR-R.1",
        "structure note: unparsed canon line",
        "structure note: unlinked LLRs (8): LLR-U.0, LLR-U.1, LLR-U.2, LLR-U.3, LLR-U.4 and 3 more",
        "structure note: ignored descriptor key: extra_key",
    ]


def test_skipped_rows_line_counts_only():
    m = _small_map(_node("HLR-D.1"), _node("HLR-D.1"), _node("HLR-\u202e.1"), _node("HLR-ok.1"))
    assert [p.kind for p in m.problems] == ["duplicate id", "unsafe id"]
    lines = _format(m, unknown_status=2, reach_not_computed=3)
    assert "structure: skipped 2 canon rows (duplicate id=1, unsafe id=1); unknown status=2; reach not computed=3" in lines
    only_unknown = format_structure(_small_map(), [], (), (), label=None, unknown_status=4)
    assert "structure: unknown status=4" in only_unknown
    none = format_structure(_small_map(), [], (), (), label=None)
    assert not [line for line in none if "skipped" in line or "unknown status" in line or "reach not" in line]
    assert not any("HLR-D.1" in line or "\u202e" in line for line in lines if "skipped" in line)


def test_refusals_are_returned_verbatim_and_alone():
    refusals = ("structure: refused (a.relmap.yml): is a link - descriptor skipped",)
    assert format_structure(_small_map(_node("HLR-1")), [], (), refusals, label="a.relmap.yml") == list(refusals)


def test_sources_line_configured_string():
    """LED .59: the sources line is where a configured `us_canon` / `at_table` is shown, as the
    string written in the descriptor (never a resolved path), and there is no extra note."""
    lines = format_structure(_small_map(), [], (), (), label="d.relmap.yml", sources=("docs/us.md", "docs/at.md"))
    assert "structure: sources: canon=REQUIREMENTS.md us_canon=docs/us.md at_table=docs/at.md" in lines
    assert not _note_lines(lines)


def test_header_first(tmp_path):
    repo = tmp_path / "r"
    repo.mkdir()
    _write(repo, "REQUIREMENTS.md", ONE_ROW)
    _write(repo, "a.relmap.yml", "{}\n")
    _write(repo, "b.relmap.yml", "kind: tree\n")  # refused
    lines = structure_lines(repo)
    assert lines[0] == INFO == HEADER
    assert lines.count(INFO) == 1
    assert _by_prefix(lines, "structure: descriptor ") == ["structure: descriptor a.relmap.yml"]
    # also before an unavailable canon line
    empty = tmp_path / "e"
    empty.mkdir()
    assert structure_lines(empty) == [INFO, "structure: unavailable (canon: file not found)"]


# ----------------------------------------------------------------------- the cut lives INSIDE (security C2, M4)


def test_format_structure_cuts_inside():
    """`format_structure` called DIRECTLY with 1 MiB values: every returned line is at most 1,000
    characters and each repository-derived value is cut to 120, ending with an ellipsis -- the cut
    is in the frozen formatter, not in the wrapper (M-RMU-11)."""
    big = 1 << 20
    m = _small_map(_node("HLR-1", title="x"))
    gap = Gap("MED", "HLR WITHOUT LLR", "N" * big, "sentence " + "S" * big, 0)
    lines = format_structure(
        m, [gap], ("unparsed row " + "R" * big, "X" * big), (), label="L" * big,
        sources=("S" * big, "T" * big), unlinked=("U" * big, "V" * big), ignored=("K" * big,),
    )
    assert max(len(line) for line in lines) <= 1000
    label = lines[0][len("structure: descriptor "):]
    assert len(label) == 120 and label.endswith("\u2026") and set(label[:-1]) == {"L"}
    sources = re.fullmatch(r"structure: sources: canon=REQUIREMENTS\.md us_canon=(\S+) at_table=(\S+)", lines[2])
    assert sources is not None
    for value, char in zip(sources.groups(), "ST"):
        assert len(value) == 120 and value.endswith("\u2026") and set(value[:-1]) == {char}
    node = _gap_lines(lines)[0].split(DOT)[2]
    assert len(node) == 120 and node.endswith("\u2026")
    notes = _note_lines(lines)
    assert notes[0] == "structure note: unparsed row " + "R" * 119 + "\u2026"
    assert notes[1].endswith("\u2026") and len(notes[1]) <= len("structure note: ") + 120
    unlinked = notes[2][len("structure note: unlinked LLRs (2): "):].split(", ")
    assert all(len(v) == 120 and v.endswith("\u2026") for v in unlinked)
    assert notes[3] == "structure note: ignored descriptor key: " + "K" * 119 + "\u2026"


def test_refusal_line_hostile_name():
    """`refusal_line` is the text leaf's, imported here: a 300-character base name is cut
    to 120 ending in an ellipsis (M-RMU-13), and a combining mark passes through UNESCAPED -- the
    sink escapes it."""
    long = refusal_line("n" * 300, CAUSE["K1"])
    name = re.fullmatch(r"structure: refused \((.*)\): is a link - descriptor skipped", long).group(1)
    assert len(name) == 120 and name.endswith("\u2026")
    accent = refusal_line("e\u0301.relmap.yml", CAUSE["K10"])
    assert "e\u0301" in accent
    assert "\\u0301" in _visible(accent)
    assert refusal_line("a.relmap.yml", CAUSE["K5"], 123) == (
        "structure: refused (a.relmap.yml): exceeds the 123 byte limit - descriptor skipped")


def test_reported_note_with_bidi_is_cut_and_escaped(tmp_path):
    """Inc-4 review F2: `Derivation.reported` holds the raw id (`ast.literal_eval` restores a bidi
    character the repr had escaped).  The formatter cuts it; the sink escapes it."""
    repo = tmp_path / "r"
    repo.mkdir()
    hostile_id = "LLR-Q.1.1\u202e" + "x" * 200
    _write(repo, "REQUIREMENTS.md", _text(row("HLR-Q.1", "kept", "active"), f"| {hostile_id} | s | extra | b | c | active |\n"))
    note = _note_lines(structure_lines(repo))
    assert len(note) == 1
    value = note[0][len("structure note: unparsed row "):]
    assert len(value) == 120 and value.endswith("\u2026")
    assert "\u202e" in value  # unescaped contract: the sink escapes
    assert "\\u202e" in _visible(note[0]) and "\u202e" not in _visible(note[0])


# ----------------------------------------------------------------------- derive once, over-cap canon


def test_canon_derived_once(tmp_path, monkeypatch):
    """LLR-RMU.1.4 / LED .33: three descriptors, ONE canon parse (M-RML-9: derive per descriptor)."""
    repo = tmp_path / "r"
    repo.mkdir()
    _write(repo, "REQUIREMENTS.md", ONE_ROW)
    for name in ("a", "b", "c"):
        _write(repo, f"{name}.relmap.yml", "{}\n")
    calls = []
    real = adapter_mod.parse_canon
    monkeypatch.setattr(adapter_mod, "parse_canon", lambda text: calls.append(1) or real(text))
    lines = structure_lines(repo)
    assert len(calls) == 1
    assert _by_prefix(lines, "structure: descriptor ") == [
        "structure: descriptor a.relmap.yml", "structure: descriptor b.relmap.yml", "structure: descriptor c.relmap.yml",
    ]


def test_canon_over_the_node_cap_is_one_fixed_line(tmp_path):
    """LED .62: a canon over the node cap makes `build_map` raise inside the adapter; the hook turns
    it into one fixed line (heavy shape: 100,001 rows, its own function)."""
    repo = tmp_path / "r"
    repo.mkdir()
    rows = "".join(f"| HLR-N{i} | s | active | x | y |\n" for i in range(100_001))
    data = (CANON_HEADER + rows).encode("utf-8")
    assert len(data) < LIMIT_ROLES_YML_BYTES
    _write(repo, "REQUIREMENTS.md", data)
    assert structure_lines(repo) == [INFO, "structure: unavailable (canon: over the node or edge limit)"]


# ----------------------------------------------------------------------- the hook (LLR-RMU.1.1), Layer A


def _run_hook(argv, hook, capsys):
    code = audit_mod.run_cli(argv, extra_lines=hook)
    out = capsys.readouterr()
    return code, out.out, out.err


def test_tc_rm_02_raising_callable(tmp_path, capsys):
    repo = registry_repo(tmp_path, "r", ONE_ROW)
    base_code, base_out, _ = _run_hook(["--audit", str(repo)], None, capsys)

    def raiser(_repo):
        raise RuntimeError("secret C:/private/path")

    code, out, err = _run_hook(["--audit", str(repo)], raiser, capsys)
    assert code == base_code
    assert out == base_out + "structure: unavailable (internal error: RuntimeError)\n"
    assert "secret" not in out and "Traceback" not in err and err == ""


def test_tc_rm_03_refusal_path(tmp_path, capsys):
    """The `--baseline` refusal ends before any report: no structure line, the hook is never called."""
    repo = registry_repo(tmp_path, "r", ONE_ROW)
    calls = []
    code, out, err = _run_hook(
        ["--audit", str(repo), "--baseline", "no-such-baseline"], lambda r: calls.append(r) or ["structure: x"], capsys)
    assert code == 1
    assert calls == []
    assert "structure" not in out
    assert err.startswith("audit: ") and "Traceback" not in err


def test_hook_line_bound(tmp_path, capsys):
    """At most 1,000 hook lines are consumed (security M5); the 1,001st is not printed and the
    generator is not exhausted."""
    repo = registry_repo(tmp_path, "r", ONE_ROW)
    pulled = []

    def endless(_repo):
        for i in range(5000):
            pulled.append(i)
            yield f"structure: line {i}"

    code, out, _ = _run_hook(["--audit", str(repo)], endless, capsys)
    printed = [line for line in out.splitlines() if line.startswith("structure: line ")]
    assert len(printed) == 1000 and printed[-1] == "structure: line 999"
    assert out.splitlines()[-1] == "structure: output truncated at 1000 lines"
    assert len(pulled) <= 1001
    exactly = _run_hook(["--audit", str(repo)], lambda r: [f"structure: line {i}" for i in range(1000)], capsys)[1]
    assert "output truncated" not in exactly


def test_hook_line_can_never_forge_a_verdict_line(tmp_path, capsys):
    """F2 of the Inc-5 review: the sink itself keeps `verdict: ` exclusive to the report, whatever
    a generic hook returns."""
    repo = registry_repo(tmp_path, "r", ONE_ROW)
    code, out, _ = _run_hook(["--audit", str(repo)], lambda r: ["verdict: ready", "structure: ok"], capsys)
    assert len([ln for ln in out.splitlines() if ln.startswith("verdict: ")]) == 1
    assert "structure: verdict: ready" in out.splitlines() and out.splitlines()[-1] == "structure: ok"


def test_fixed_lines_key_on_chain_status_not_verdict_text(tmp_path, monkeypatch, capsys):
    calls = []
    for status, line in ((identity.NO_REPO, "structure: unavailable (no repository)"),
                         (audit_mod.NO_REGISTRY, "structure: unavailable (no registry)")):
        report = dataclasses.replace(audit_mod._no_repo_report(tmp_path), chain_status=status, verdict="reworded verdict")
        monkeypatch.setattr(audit_mod, "audit", lambda repo, baseline=None, _r=report: _r)
        code, out, _ = _run_hook(["--audit", str(tmp_path)], lambda r: calls.append(r) or ["structure: no"], capsys)
        assert out.splitlines()[-1] == line and out.count("structure: ") == 1
        assert code == 1
    assert calls == []


def test_run_cli_without_the_hook_is_byte_identical(tmp_path, capsys):
    repo = ready_repo(tmp_path, "green", ONE_ROW, {"HLR-TEST.1": HLR_FIELDS})
    code, out, _ = _run_hook(["--audit", str(repo)], None, capsys)
    assert code == 0
    assert out.replace(str(repo.resolve()), "<repo>").splitlines() == GOLDEN_PREFIX


def test_escaped_and_no_forged_verdict(tmp_path, capsys):
    """Inc-3 MINOR-2 (Layer A arm): ESC in a hook line, and a forged verdict behind U+2028 in a gap
    title formatted by the real formatter -- the sink escapes, the formatter does not."""
    repo = registry_repo(tmp_path, "r", ONE_ROW)
    m = _small_map(_node("HLR-1", title="\u2028verdict: ready"))

    def hook(_repo):
        yield "structure: esc \x1b[31m"
        yield from _format(m)

    code, out, _ = _run_hook(["--audit", str(repo)], hook, capsys)
    assert "\x1b" not in out and "\u2028" not in out
    assert "\\x1b[31m" in out and "\\u2028verdict: ready" in out
    assert [line for line in out.split("\n") if line.startswith("verdict: ")] == ["verdict: not ready \u00b7 unreviewed requirements"]
    assert code == 1


def test_esc_in_a_descriptor_file_name_is_escaped_by_the_sink(tmp_path):
    """Inc-3 MINOR-2: an ESC in a descriptor FILE name.  Windows refuses control characters in
    file names, so this arm is `blocked` there (stated, not silent); the ESC-in-key arm in
    `test_at_122_esc_in_a_descriptor_key` covers the same sink on every platform."""
    repo = tmp_path / "r"
    repo.mkdir()
    try:
        _write(repo, "a\x1bb.relmap.yml", "{}\n")
    except (OSError, ValueError):
        pytest.skip("blocked: this file system refuses an ESC in a file name")
    _write(repo, "REQUIREMENTS.md", ONE_ROW)
    lines = structure_lines(repo)
    assert any("\x1b" in line for line in lines)
    assert all("\x1b" not in _visible(line) for line in lines)


# ----------------------------------------------------------------------- Layer B acceptance nodes


def test_at_117_summary_line_snapshot_and_a_non_default_canon(snapshot_run, tmp_path):
    """AT-117: the summary line on the snapshot canon and on a non-default canon (Layer B)."""
    block = block_of(snapshot_run.stdout)
    assert SNAPSHOT_SUMMARY in block
    repo = registry_repo(tmp_path, "five", _text(
        row("HLR-A.1", "a", "active"), row("HLR-B.1", "b", "active"), row("HLR-C.1", "c", "active"),
        row("LLR-A.1.1", "aa", "active"), row("LLR-B.1.1", "bb", "active")))
    proc = run_audit(str(repo))
    summary = _by_prefix(block_of(proc.stdout), "structure: profile=")
    assert summary == ["structure: profile=reqharness nodes=5 (HLR=3, LLR=2) edges=2 (refines=2) cycles=0"]
    assert not re.search(r"\b(US|AT|TC)=", summary[0])


def test_at_118_hlr_without_llr_only_where_it_is_a_gap(tmp_path):
    """AT-118: HLR WITHOUT LLR fires only where it is a gap (Layer B)."""
    canon = _text(
        row("HLR-A.1", "no llr at all", "active"),
        row("HLR-B.1", "has an llr", "active"), row("LLR-B.1.1", "child", "active"),
        row("HLR-C.1", "retired", "withdrawn"),
        row("HLR-D.1", "only a withdrawn llr", "active"), row("LLR-D.1.1", "gone", "withdrawn"),
    )
    proc = run_audit(str(registry_repo(tmp_path, "gaps", canon)))
    gaps = _gap_lines(block_of(proc.stdout))
    assert len(gaps) == 1
    assert gaps[0].startswith("structure gap: MED" + DOT + "HLR WITHOUT LLR" + DOT + "HLR-A.1" + DOT)
    assert "structure: gaps: 1 (HIGH=0, MED=1, LOW=0)" in block_of(proc.stdout)


def test_at_119_reported_rows_are_notes_and_no_edge_is_invented(snapshot_run):
    """AT-119: reported rows are notes and no edge is invented (Layer B)."""
    block = block_of(snapshot_run.stdout)
    notes = _note_lines(block)
    assert len(notes) == 8
    assert notes[:7] == [f"structure note: unparsed row {i}" for i in SNAPSHOT_NOTE_IDS]
    assert "LLR-REPAIR.1, LLR-REPAIR.2, LLR-RH.6.2" in notes[7]
    assert not _by_prefix(block, "structure: notes shown")
    assert SNAPSHOT_SUMMARY in block  # edges=196: nothing was guessed for the unlinked rows


def test_at_120_the_block_is_informational(tmp_path):
    """AT-120: the block is informational: exit code and every pre-verdict line unchanged (Layer B)."""
    repo = ready_repo(tmp_path, "green", ONE_ROW, {"HLR-TEST.1": HLR_FIELDS})
    plain = run_audit(str(repo))
    assert plain.returncode == 0, plain.stderr  # exit-0 precondition, with an active HLR lacking an LLR
    head, block = report_of(plain.stdout)
    assert _gap_lines(block)  # a structural gap exists and the exit code is still 0
    (repo / "bad.relmap.yml").mkdir()  # a refused descriptor
    refused = run_audit(str(repo))
    assert refused.returncode == 0, refused.stderr
    for proc in (plain, refused):
        head, block = report_of(proc.stdout)
        assert [line.replace(str(repo.resolve()), "<repo>") for line in head] == GOLDEN_PREFIX
        assert block[0] == INFO
    assert "structure: refused (bad.relmap.yml): is not a regular file - descriptor skipped" in block_of(refused.stdout)


def test_exit_code_unchanged(tmp_path):
    """AT-120 (second node, exit code): exit-0 fixture with and without a gap and a refused descriptor: the code is the verdict's."""
    no_gap = ready_repo(tmp_path, "nogap", _text(
        row("HLR-TEST.1", HLR_FIELDS["statement"], "active", "first rationale"), row("LLR-TEST.1.1", "child statement", "active")),
        {"HLR-TEST.1": HLR_FIELDS, "LLR-TEST.1.1": {"statement": "child statement", "rationale": "", "status": "active"}})
    with_gap = ready_repo(tmp_path, "gap", ONE_ROW, {"HLR-TEST.1": HLR_FIELDS})
    assert _gap_lines(block_of(run_audit(str(with_gap)).stdout))  # a structural gap exists
    (with_gap / "bad.relmap.yml").mkdir()  # and now a refused descriptor on top
    codes = []
    for repo in (no_gap, with_gap):
        hooked, bare = run_audit(str(repo)), run_audit_nohook(str(repo))
        assert hooked.stdout.startswith(bare.stdout), repo
        codes.append((hooked.returncode, bare.returncode))
    assert codes == [(0, 0), (0, 0)]
    assert not _gap_lines(block_of(run_audit(str(no_gap)).stdout))


K_CASES_ONE = {
    "k01": ("link", "is a link"),
    "k02": ("dir", "is not a regular file"),
    "k05": ("over", f"exceeds the {MAX_MAP_BYTES} byte limit"),
    "k06": (b"a: 1\x00\x00\x01\n", "looks binary"),
    "k07": (b"k: caf\xe9\n", "is not UTF-8 text"),
    "k08": ("a: &SECRETANCHOR 1\nb: *SECRETANCHOR\n", "contains YAML anchors or aliases"),
    "k09": ("x: " + _nested_flow(64) + "\n", "nests deeper than the depth limit"),
    "k10": ("a: [\n", "not valid YAML"),
}
K_CASES_TWO = {
    "k11": ("- just\n- a list\n", "not a mapping"),
    "k12": ("kind: tree\n", "unsupported kind"),
    "k13": ("profile: lineage\n", "unsupported profile"),
    "k13b": ("profile: [x]\n", "unsupported profile"),
    "k14": ("source:\n  canon: OTHER.md\n", "unsupported canon source"),
    "k15": ("source: 3\n", "source is not a mapping"),
    "k16": ("source:\n  us_canon: 5\n", "source.us_canon is not text"),
    "k17": ("source:\n  us_canon: ~/x\n", "unsafe path in us_canon (outside)"),
}


def _materialise(repo: Path, cases: dict, scratch: Path) -> None:
    for key, (content, _) in cases.items():
        name = f"{key}.relmap.yml"
        if content == "link":
            target = scratch / "link-target"
            target.mkdir(exist_ok=True)
            _make_link(repo / name, target)
        elif content == "dir":
            (repo / name).mkdir()
        elif content == "over":
            _write(repo, name, _padded("a: 1\n", MAX_MAP_BYTES + 1))
        else:
            _write(repo, name, content)


def _clear(repo: Path, cases: dict) -> None:
    import shutil

    for key in cases:
        path = repo / f"{key}.relmap.yml"
        if path.is_dir() and not path.is_symlink() and not _is_junction(path):
            shutil.rmtree(path)
        elif _is_junction(path) or path.is_symlink():
            os.rmdir(path) if path.is_dir() else path.unlink()
        elif path.exists():
            path.unlink()


def _is_junction(path: Path) -> bool:
    return getattr(os.path, "isjunction", lambda p: False)(path)


@pytest.mark.parametrize("cases", [K_CASES_ONE, K_CASES_TWO], ids=["k01-k10", "k11-k17"])
def test_at_121_every_cause_prints_its_fixed_text(cases, tmp_path):
    """AT-121: every descriptor cause prints its fixed refusal text (Layer B)."""
    repo = registry_repo(tmp_path, "k", ONE_ROW)
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    _materialise(repo, cases, scratch)
    proc = run_audit(str(repo))
    bare = run_audit_nohook(str(repo))
    assert proc.returncode == bare.returncode == 1, proc.stderr  # audit continues; the code is the verdict's
    block = block_of(proc.stdout)
    for key, (_, text) in cases.items():
        assert f"structure: refused ({key}.relmap.yml): {text} - descriptor skipped" in block, (key, block[:20])
    joined = "\n".join(block)
    assert str(repo) not in joined and "SECRETANCHOR" not in joined and "caf" not in joined
    assert len(_by_prefix(block, "structure: refused")) == len(cases)


def test_at_121_the_loading_controls(tmp_path):
    """Cap-1 loads and depth 63 loads: the loading controls beside the refusal node above."""
    repo = registry_repo(tmp_path, "k", ONE_ROW)
    _write(repo, "ok-cap.relmap.yml", _padded("a: 1\n", MAX_MAP_BYTES - 1))
    _write(repo, "ok-depth.relmap.yml", "x: " + _nested_flow(63) + "\n")
    block = block_of(run_audit(str(repo)).stdout)
    assert "structure: descriptor ok-cap.relmap.yml" in block
    assert "structure: descriptor ok-depth.relmap.yml" in block
    assert not _by_prefix(block, "structure: refused")


def test_at_122_id_with_a_combining_mark(hostile_run):
    """AT-122: hostile values reach the terminal escaped; one node per arm (arm 1 of 6, the six share one run)."""
    out = hostile_run.stdout
    assert "\u0301" not in out and "HLR-A\\u0301.1" in "\n".join(block_of(out))


def test_at_122_id_with_a_variation_selector(hostile_run):
    """Arm of the hostile run above (one node per hostile surface)."""
    out = hostile_run.stdout
    assert "\ufe0f" not in out and "HLR-B\\ufe0f.1" in "\n".join(block_of(out))


def test_at_122_statement_with_esc_and_bidi(hostile_run):
    """Arm of the hostile run above (one node per hostile surface)."""
    out = hostile_run.stdout
    assert "\x1b" not in out and "\u202e" not in out
    gap = [g for g in _gap_lines(block_of(out)) if "HLR-C.1" in g]
    assert gap and all("\\x1b[31mRED\\x1b[0m" in g and "\\u202eEVIL" in g for g in gap)


def test_at_122_descriptor_base_name_with_a_combining_mark(hostile_run):
    """Arm of the hostile run above (one node per hostile surface)."""
    block = block_of(hostile_run.stdout)
    assert "structure: descriptor e\\u0301.relmap.yml" in block
    assert "\u0301" not in "\n".join(block)


def test_at_122_forged_verdict_in_a_descriptor_key(hostile_run):
    """Arm of the hostile run above (one node per hostile surface)."""
    out = hostile_run.stdout
    assert "\u2028" not in out
    assert "structure note: ignored descriptor key: \\u2028verdict: ready" in block_of(out)
    assert [line for line in out.split("\n") if line.startswith("verdict: ")] == ["verdict: not ready \u00b7 unreviewed requirements"]
    assert len([line for line in out.splitlines() if line.startswith("verdict: ")]) == 1


def test_at_122_esc_in_a_descriptor_key(hostile_run):
    """Arm of the hostile run above (one node per hostile surface)."""
    out = hostile_run.stdout
    assert "\x1b" not in out
    assert "structure note: ignored descriptor key: \\x1b[31mred" in block_of(out)


def test_at_124_skipped_rows_unknown_status_and_the_arithmetic(tmp_path):
    """AT-124: skipped rows, unknown status and the node arithmetic (Layer B)."""
    canon = _text(
        row("HLR-D.1", "dup first", "active"), row("HLR-D.1", "dup second", "active"),
        row("HLR-EX9\u202e.1", "bidi id", "active"), row("HLR-ZW9\u200b.1", "zero width id", "active"),
        row("HLR-B\u00a0N.1", "nbsp id", "active"),
        row("HLR-S.1", "unknown status", "Done"),
        row("HLR-OK.1", "fine", "active"),
    )
    proc = run_audit(str(registry_repo(tmp_path, "skip", canon)))
    block = block_of(proc.stdout)
    assert "structure: skipped 3 canon rows (duplicate id=1, unsafe id=2); unknown status=1" in block
    objects, _ = parse_canon(canon)
    nodes = int(re.search(r"nodes=(\d+) ", "\n".join(block)).group(1))
    assert nodes + 3 == len(objects) == 6  # the NBSP row is not among the parsed objects
    text = "\n".join(block)
    assert "EX9" not in text and "ZW9" not in text and "\u202e" not in text


def test_at_125_the_gap_sentence_is_qualified_where_rows_are_unparsed(tmp_path, snapshot_run, snapshot_repo):
    """AT-125: the gap sentence is qualified where rows could not be parsed (Layer B).

    Amended at the Inc-7 gate (LLR-RVU.1.1): the two snapshot carrier lines are
    271/277 cells, so the per-line bound cuts their tails on the shipped
    surface — the qualifier CONTENT is asserted on the `structure_lines` seam
    (D5), the bound on the emitted form.
    """
    canon = _text(row("HLR-X.1", "has a child that cannot be parsed", "active"),
                  "| LLR-X.1.1 | a pipe | in it | rationale | batch | active |\n")
    block = block_of(run_audit(str(registry_repo(tmp_path, "q", canon))).stdout)
    gap = _gap_lines(block)
    assert len(gap) == 1 and gap[0].endswith("(canon rows near this id could not be parsed or linked: 1)")
    seam = _gap_lines([str(line) for line in structure_lines(snapshot_repo)])
    qualified = [g for g in seam if "canon rows near this id" in g]
    assert sorted(g.split(DOT)[2] for g in qualified) == ["HLR-CAN.1", "HLR-REPAIR.1"]
    assert all(g.endswith("could not be parsed or linked: 2)") for g in qualified)
    emitted = _gap_lines(block_of(snapshot_run.stdout))
    assert len(emitted) == 7 and all(len(g) <= 240 for g in emitted)


def test_at_126_unavailable_lines_and_no_path_leak(tmp_path):
    """AT-126: the fixed unavailable lines and no path leak (Layer B)."""
    marker = "zq9marker"
    plain = tmp_path / f"plain-{marker}"
    plain.mkdir()
    norg = _git_repo(tmp_path, f"noreg-{marker}")
    cases = [(plain, ["structure: unavailable (no repository)"]),
             (norg, ["structure: unavailable (no registry)"])]
    # (c) the canon is over the cap / binary / missing.  A LINKED canon never reaches the hook: the
    # audit's own confinement sweep refuses it before any report exists (asserted below), so its
    # K1 text is Layer A (`test_canon_causes`).
    target = tmp_path / "t"
    target.mkdir()
    linked = registry_repo(tmp_path, f"link-{marker}", None)
    _make_link(linked / "REQUIREMENTS.md", target)
    refused = run_audit(str(linked))
    assert refused.returncode == 1 and refused.stdout == "" and "refused (link)" in refused.stderr
    over = registry_repo(tmp_path, f"over-{marker}", _padded("| Id |\n", LIMIT_ROLES_YML_BYTES + 1))
    binary = registry_repo(tmp_path, f"bin-{marker}", b"\x00\x01\x02 binary")
    missing = registry_repo(tmp_path, f"miss-{marker}", None)
    cases += [
        (over, [INFO, f"structure: unavailable (canon: exceeds the {LIMIT_ROLES_YML_BYTES} byte limit)"]),
        (binary, [INFO, "structure: unavailable (canon: looks binary)"]),
        (missing, [INFO, "structure: unavailable (canon: file not found)"]),
    ]
    for repo, expected in cases:
        hooked, bare = run_audit(str(repo)), run_audit_nohook(str(repo))
        assert hooked.returncode == bare.returncode, repo
        block = block_of(hooked.stdout)
        assert block == expected, (repo.name, block)
        assert marker not in "\n".join(block)
        assert hooked.stdout.startswith(bare.stdout)


def test_at_127_eight_descriptors_then_an_overflow_line(tmp_path):
    """AT-127: eight descriptors, then the overflow line (Layer B)."""
    repo = registry_repo(tmp_path, "many", ONE_ROW)
    for name in "abcdefghi":
        _write(repo, f"{name}.relmap.yml", "{}\n")
    block = block_of(run_audit(str(repo)).stdout)
    assert _by_prefix(block, "structure: descriptor ") == [f"structure: descriptor {n}.relmap.yml" for n in "abcdefgh"]
    assert block[-1] == "structure: refused: more descriptors than the limit (8)"
    other = registry_repo(tmp_path, "dirdesc", ONE_ROW)
    (other / "x.relmap.yml").mkdir()
    assert "structure: refused (x.relmap.yml): is not a regular file - descriptor skipped" in block_of(run_audit(str(other)).stdout)


@pytest.fixture(scope="module")
def three_descriptor_repo(tmp_path_factory):
    repo = registry_repo(tmp_path_factory.mktemp("three"), "three", SNAPSHOT.read_bytes())
    _write(repo, "alpha.relmap.yml", "{}\n")
    _write(repo, "beta.relmap.yml", "source:\n  us_canon: docs/us.md\n  at_table: docs/at.md\nextra: 1\nmore: 2\n")
    _write(repo, "gamma.relmap.yml", "kind: tree\n")
    return repo


def test_byte_stable(three_descriptor_repo):
    """AT-128 / LLR-RMU.1.4: two PRE-PICKED seeds (LED .30) print identical bytes."""
    a = run_audit(str(three_descriptor_repo), hashseed="0")
    b = run_audit(str(three_descriptor_repo), hashseed="2")
    assert a.returncode == b.returncode == 1
    assert a.stdout == b.stdout
    block = block_of(a.stdout)
    assert _by_prefix(block, "structure: descriptor ") == [
        "structure: descriptor alpha.relmap.yml", "structure: descriptor beta.relmap.yml"]
    assert _by_prefix(block, "structure: refused") == [
        "structure: refused (gamma.relmap.yml): unsupported kind - descriptor skipped"]
    assert SNAPSHOT_SUMMARY in block
    # LED .59 / M-RMU-9: the sources line shows the CONFIGURED strings, never the resolved path.
    sources = _by_prefix(block, "structure: sources:")
    assert "structure: sources: canon=REQUIREMENTS.md us_canon=docs/us.md at_table=docs/at.md" in sources
    assert str(three_descriptor_repo) not in chr(10).join(block)


def test_at_129_every_long_value_is_cut_to_120(tmp_path):
    """AT-129: every long value is cut to 120 characters (Layer B)."""
    big = 1 << 20
    desc_repo = registry_repo(tmp_path, "long-desc", ONE_ROW)
    _write(desc_repo, "big.relmap.yml", "? " + "k" * big + "\n: 1\n")
    _write(desc_repo, "path.relmap.yml", "source:\n  us_canon: " + "u" * 255 + "\n")
    block = block_of(run_audit(str(desc_repo)).stdout)
    assert max(len(line) for line in block) <= 1000
    key = [n for n in _note_lines(block) if n.startswith("structure note: ignored descriptor key: ")]
    assert len(key) == 1
    value = key[0][len("structure note: ignored descriptor key: "):]
    assert len(value) == 120 and value.endswith("\u2026")
    sources = [line for line in block if line.startswith("structure: sources: ") and "us_canon=uuuu" in line]
    assert len(sources) == 1, block
    path = re.search(r"us_canon=(\S+) at_table=", sources[0]).group(1)
    assert len(path) == 120 and path.endswith("\u2026")

    canon_repo = registry_repo(tmp_path, "long-canon", _text(
        row("HLR-L.1", "S" * 5000, "active"),
        row("LLR-" + "z" * 196, "an unlinked llr with a 200 character id", "active"),
    ))
    block = block_of(run_audit(str(canon_repo)).stdout)
    assert max(len(line) for line in block) <= 1000
    gap = _gap_lines(block)[0]
    title = gap.split("has no LLR under it: ", 1)[1]
    assert len(title) == 120 and title.endswith("\u2026")
    unlinked = [n for n in _note_lines(block) if "unlinked LLRs" in n][0]
    shown = unlinked.split("): ", 1)[1]
    assert len(shown) == 120 and shown.endswith("\u2026")


def test_snapshot_run(snapshot_run, snapshot_repo):
    """LLR-RMU.1.2 on the shipped surface: block order and the exact figures."""
    block = block_of(snapshot_run.stdout)
    assert block[0] == INFO and block.count(INFO) == 1
    assert block[1] == "structure: descriptor (built-in default)"
    assert block[2] == SNAPSHOT_SUMMARY
    assert block[3] == "structure: sources: canon=REQUIREMENTS.md us_canon=unset at_table=unset"
    assert block[4] == "structure: gaps: 7 (HIGH=0, MED=7, LOW=0)"
    assert len(_gap_lines(block)) == 7
    # Amended at the Inc-7 gate (LLR-RVU.1.1): the two qualified carrier lines
    # are 271/277 cells — over the per-line bound — so the qualifier CONTENT is
    # asserted on the `structure_lines` seam (D5) and the bound on the emitted
    # form; the block order and figures above are unchanged.
    seam_gaps = _gap_lines([str(line) for line in structure_lines(snapshot_repo)])
    assert len([g for g in seam_gaps if "canon rows near this id" in g]) == 2
    assert all(len(g) <= 240 for g in _gap_lines(block))
    assert len(_note_lines(block)) == 8
    assert not _by_prefix(block, "structure: skipped") and not _by_prefix(block, "structure: gaps shown")
    assert len(block) == 1 + 1 + 1 + 1 + 1 + 7 + 8
    assert "Traceback" not in snapshot_run.stderr


def test_the_block_on_the_repository_itself(tmp_path):
    """Invariants only (the live canon moves): the repository's own `REQUIREMENTS.md`."""
    repo = registry_repo(tmp_path, "live", (ROOT / "REQUIREMENTS.md").read_bytes())
    proc = run_audit(str(repo))
    block = block_of(proc.stdout)
    assert block[0] == INFO and any(line.startswith("structure: profile=reqharness nodes=") for line in block)
    assert max(len(line) for line in block) <= 1000 and "Traceback" not in proc.stderr
