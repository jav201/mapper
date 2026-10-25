"""HLR-RMA.1 / LLR-RMA.1.1-.1.4, LLR-RMG.1.2 (snapshot arm) -- the canon adapter.

`mapper/relmap/adapter.py` derives the `reqharness` relation map read-only from the canon.  Two
inputs, two kinds of oracle (ruling R4):

* the FROZEN snapshot `tests/fixtures/relmap/REQUIREMENTS.snapshot.md` (the canon at the P1 base,
  pinned by an LF-normalised sha256) carries the EXACT figures -- 275 nodes, 196 edges, 7 reported
  rows, 3 unlinked, 7 gaps;
* the LIVE `REQUIREMENTS.md` is checked by invariants against an independent line counter and its
  figures are never pinned (a living file moves on the next unrelated edit).

This module is also the in-process Layer A stand-in for AT-117/AT-119/AT-124/AT-125: the layer B
arms run `mapper --audit` through the hook that lands in Inc-5 (proposal 2.1 *Layer phasing*).
There is NO elapsed-time assertion.
"""
from __future__ import annotations

import builtins
import hashlib
import io
import os
import re
import subprocess
from pathlib import Path

import pytest

import mapper
from mapper.relmap import adapter as amod
from mapper.relmap import descriptor as dmod
from mapper.relmap.adapter import CanonUnavailable, Derivation, derive_reqharness_map
from mapper.relmap.descriptor import CAUSE, Descriptor, default_descriptor
from mapper.relmap.gaps import detect_gaps
from mapper.reqharness.derive import LIMIT_ROLES_YML_BYTES, parse_canon

ROOT = Path(mapper.__file__).resolve().parent.parent
SNAPSHOT = ROOT / "tests" / "fixtures" / "relmap" / "REQUIREMENTS.snapshot.md"
LEDGER = ROOT / ".dev-flow" / "2026-10-25-relmap-r1-batch" / "01-requirements-ledger.md"

# The AUTHORITATIVE pin: sha256 of `git show HEAD:REQUIREMENTS.md` at the P1 base, newlines
# normalised to LF (ledger .36 corrects .4: 93b18472... is the digest of the CRLF working copy).
SNAPSHOT_SHA256 = "b093c9203f0fe75f218298f56cc723a812902a1f4979424c8c2cb931bd39a25a"

HEADER = "| Id | Status | Statement |\n|---|---|---|\n"


def lf_sha256(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def canon(*rows: str) -> str:
    return HEADER + "".join(r + "\n" for r in rows)


def row(row_id: str, status: str = "active", statement: str = "text") -> str:
    return f"| {row_id} | {status} | {statement} |"


def repo_with(tmp_path: Path, text: str | bytes) -> Path:
    data = text.encode("utf-8") if isinstance(text, str) else text
    (tmp_path / "REQUIREMENTS.md").write_bytes(data)
    return tmp_path


def derive(repo: Path, descriptor: Descriptor | None = None) -> Derivation:
    return derive_reqharness_map(repo, descriptor or default_descriptor())


@pytest.fixture(scope="module")
def snapshot_derivation(tmp_path_factory) -> Derivation:
    repo = tmp_path_factory.mktemp("snapshot")
    (repo / "REQUIREMENTS.md").write_bytes(SNAPSHOT.read_bytes())
    return derive(repo)


# ------------------------------------------------------------------ the snapshot pin (PD-1)


def test_snapshot_sha256():
    assert lf_sha256(SNAPSHOT.read_bytes()) == SNAPSHOT_SHA256


def test_snapshot_sha256_crlf_arm():
    """A CRLF-rewritten copy (what a Windows checkout without `-text` would hold) gives the same pin."""
    crlf = SNAPSHOT.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    assert crlf != SNAPSHOT.read_bytes().replace(b"\r\n", b"\n")
    assert lf_sha256(crlf) == SNAPSHOT_SHA256


def test_snapshot_pin_matches_the_ledger_while_the_batch_folder_exists():
    if not LEDGER.exists():
        pytest.skip("n/a - the batch folder is not in this checkout")
    text = LEDGER.read_text(encoding="utf-8")
    assert "batch.36 " in text, "the ledger heading for the snapshot pin is missing or reworded"
    assert SNAPSHOT_SHA256 in text.split("batch.36 ", 1)[1].split("### LED-", 1)[0]


def test_gitattributes_keeps_the_fixture_bytes():
    lines = (ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()
    assert "tests/fixtures/relmap/** -text" in [ln.strip() for ln in lines]


# ------------------------------------------------------------------ LLR-RMA.1.1 / .1.2 / .1.3 on the snapshot


def test_snapshot_census(snapshot_derivation):
    m = snapshot_derivation.map
    assert len(m.nodes) == 275
    assert sum(1 for n in m.nodes if n.kind == "HLR") == 76
    assert sum(1 for n in m.nodes if n.kind == "LLR") == 199
    assert len(m.edges) == 196
    assert {e.type for e in m.edges} == {"refines"}
    assert m.nodes[0].id == "HLR-CNV.1"
    assert m.problems == () and m.cycles == ()
    assert snapshot_derivation.unknown_status == 0
    assert {n.status for n in m.nodes} <= amod.STATUS_WORDS
    assert m.sourced == frozenset({"HLR", "LLR"})
    assert {n.id for n in m.nodes}.isdisjoint({"HLR-RH.6", "LLR-RH.6.1"})


def test_snapshot_structure_figures(snapshot_derivation):
    """The figures AT-117, AT-119 and AT-125 will print, asserted in process (Layer A)."""
    d = snapshot_derivation
    assert d.reported == (
        "unparsed row LLR-HYG.1.1",
        "unparsed row LLR-CAN.1.1",
        "unparsed row LLR-CAN.1.2",
        "unparsed row HLR-RH.6",
        "unparsed row LLR-RH.6.1",
        "unparsed row LLR-RH.7.3",
        "unparsed row LLR-Q3.1.2",
    )
    assert d.unlinked == ("LLR-REPAIR.1", "LLR-REPAIR.2", "LLR-RH.6.2")
    assert len(d.reported) + 1 == 8  # seven report notes and one unlinked-list note (AT-119)
    assert len(d.map.nodes) + len(d.reported) == 275 + 7


def test_snapshot_unparsed_counts(snapshot_derivation):
    m = snapshot_derivation.map
    assert m.node("HLR-CAN.1").unparsed == 2  # LLR-CAN.1.1, LLR-CAN.1.2 (starts-with branch)
    assert m.node("HLR-REPAIR.1").unparsed == 2  # LLR-REPAIR.1, LLR-REPAIR.2 (sibling-stem branch)
    nonzero = {n.id for n in m.nodes if n.unparsed}
    assert {"HLR-CAN.1", "HLR-REPAIR.1"} <= nonzero


def test_snapshot_gaps(snapshot_derivation):
    """LLR-RMG.1.2 snapshot arm: 7 gaps, all `HLR WITHOUT LLR`; the US/AT/TC rows stay silent
    because those kinds are unsourced; the qualifier sits on HLR-CAN.1 and HLR-REPAIR.1 only."""
    m = snapshot_derivation.map
    gaps = detect_gaps(m)
    assert len(gaps) == 7
    assert {g.kind for g in gaps} == {"HLR WITHOUT LLR"}
    qualified = {g.node: g.sentence for g in gaps if "could not be parsed or linked" in g.sentence}
    assert set(qualified) == {"HLR-CAN.1", "HLR-REPAIR.1"}
    for sentence in qualified.values():
        assert sentence.endswith("(canon rows near this id could not be parsed or linked: 2)")
    for g in gaps:
        if g.node not in qualified:
            assert m.node(g.node).unparsed == 0
    assert not any(g.kind in {"US WITHOUT AT", "LLR NOT VERIFIED", "ORPHAN TC", "OPEN AT WITHOUT TEST"}
                   for g in gaps)


# ------------------------------------------------------------------ the LIVE canon: invariants only


def _counted_rows(text: str) -> tuple[list[str], list[str]]:
    """(ids of HLR/LLR table rows after the first `Id` header, ids of those whose cell count differs).

    An independent line counter: it shares no code with `parse_canon` or the adapter.
    """
    width = None
    ids: list[str] = []
    short: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if width is None:
            if cells[0].lower() == "id" and "status" in [c.lower() for c in cells]:
                width = len(cells)
            continue
        if re.fullmatch(r"(HLR|LLR)-\S+", cells[0]):
            ids.append(cells[0])
            if len(cells) != width:
                short.append(cells[0])
    return ids, short


def test_live_invariants(tmp_path):
    live = (ROOT / "REQUIREMENTS.md").read_bytes()
    d = derive(repo_with(tmp_path, live))
    m = d.map
    ids, short = _counted_rows(live.decode("utf-8"))
    assert len(ids) > 0 and len(short) == len(d.reported) - sum(r == amod.NOTE_UNPARSED_LINE for r in d.reported)
    # every counted row is a node, a reported row, or a problem (duplicate / unsafe id)
    assert len(m.nodes) + len(short) + len(m.problems) == len(ids)
    node_ids = {n.id for n in m.nodes}
    assert node_ids.isdisjoint(short)
    llrs = [n for n in m.nodes if n.kind == "LLR"]
    assert len(m.edges) + len(d.unlinked) == len(llrs)
    for e in m.edges:
        assert e.type == "refines"
        assert e.src == "HLR-" + e.dst[len("LLR-"):].rsplit(".", 1)[0]
        assert m.node(e.src).kind == "HLR"
    assert set(d.unlinked) <= node_ids
    assert d.reported == tuple(f"unparsed row {i}" for i in short)
    assert m.cycles == ()


def test_live_invariants_see_a_dropped_row(tmp_path):
    """The invariant is not vacuous: the counter and a derivation that loses a row disagree."""
    live = (ROOT / "REQUIREMENTS.md").read_text(encoding="utf-8")
    ids, short = _counted_rows(live)
    d = derive(repo_with(tmp_path, live))
    assert len(d.map.nodes) + len(short) + len(d.map.problems) == len(ids)
    assert len(d.map.nodes) - 1 + len(short) + len(d.map.problems) != len(ids)


# ------------------------------------------------------------------ LLR-RMA.1.1 nodes


def test_status_words(tmp_path):
    text = canon(
        row("HLR-A.1", "Active"),
        row("HLR-A.2", "active (partial)"),
        row("HLR-A.3", ""),
        row("HLR-A.4", "done"),
        row("HLR-A.5", "Withdrawn"),
        row("HLR-A.6", "SPLIT into two"),
    )
    d = derive(repo_with(tmp_path, text))
    status = {n.id: n.status for n in d.map.nodes}
    assert status == {"HLR-A.1": "active", "HLR-A.2": "active", "HLR-A.3": "", "HLR-A.4": "done",
                      "HLR-A.5": "withdrawn", "HLR-A.6": "split"}
    assert d.unknown_status == 2  # the empty word and `done`: kept, counted, ineligible
    assert {g.node for g in detect_gaps(d.map)} == {"HLR-A.1", "HLR-A.2"}  # only `active` is eligible


def test_node_fields(tmp_path):
    long = "x" * 130
    d = derive(repo_with(tmp_path, canon(row("HLR-B.1", "active", f"  a   spaced\tstatement "),
                                         row("LLR-B.1.1", "active", long))))
    first, second = d.map.nodes
    assert (first.kind, first.title, first.open) == ("HLR", "a spaced statement", False)
    assert second.kind == "LLR" and len(second.title) == 120 and second.title.endswith("…")
    assert second.title[:119] == "x" * 119


def test_nodes_in_canon_order(tmp_path):
    d = derive(repo_with(tmp_path, canon(row("LLR-C.1.1"), row("HLR-C.1"), row("HLR-A.1"))))
    assert [n.id for n in d.map.nodes] == ["LLR-C.1.1", "HLR-C.1", "HLR-A.1"]


def test_empty_canon_is_an_empty_map(tmp_path):
    for text in ("", "no table here\n", HEADER):
        d = derive(repo_with(tmp_path, text))
        assert d.map.nodes == () and d.map.edges == ()
        assert (d.reported, d.unlinked, d.unknown_status) == ((), (), 0)


def test_unsourced_kinds_keep_their_gap_kinds_inactive(tmp_path):
    d = derive(repo_with(tmp_path, canon(row("HLR-D.1"), row("LLR-D.1.1"))))
    assert d.map.sourced == frozenset({"HLR", "LLR"})
    assert detect_gaps(d.map) == []  # `LLR NOT VERIFIED` would fire on LLR-D.1.1 if TC were sourced
    assert {n.kind for n in d.map.nodes} == {"HLR", "LLR"}


def test_duplicate_and_unsafe_ids_are_counted_never_linked(tmp_path):
    """AT-124, Layer A: a duplicate id, two unsafe ids (U+202E, U+200B), an NBSP id (not a canon row),
    one `Done` status."""
    text = canon(
        row("HLR-E.1"),
        row("LLR-E.1.1"),
        row("LLR-E.1.1"),  # duplicate id
        row("LLR-E.1.2\u202e"),  # unsafe
        row("LLR-E.1.3\u200b"),  # unsafe
        row("LLR-E.1.4\u00a0x"),  # NBSP: skipped by the canon reader, not a parsed row
        row("LLR-E.1.5", "Done"),
    )
    parsed, reported = parse_canon(text)
    assert reported == () and len(parsed) == 6
    d = derive(repo_with(tmp_path, text))
    kinds = sorted(p.kind for p in d.map.problems)
    assert kinds == ["duplicate id", "unsafe id", "unsafe id"]
    assert len(d.map.nodes) + len(d.map.problems) == len(parsed)
    assert d.unknown_status == 1
    assert [(e.src, e.dst) for e in d.map.edges] == [("HLR-E.1", "LLR-E.1.1"), ("HLR-E.1", "LLR-E.1.5")]
    assert d.unlinked == ()
    assert all(p.kind != "unknown endpoint" for p in d.map.problems)


def test_unknown_status_counts_kept_nodes_only(tmp_path):
    """Ledger .61, AT-124 Layer A: a duplicate-id row whose status is `done` is excluded by the
    builder, so it is not counted; only the kept `Done` row is."""
    text = canon(
        row("HLR-G.1"),
        row("LLR-G.1.1", "active"),
        row("LLR-G.1.1", "done"),  # duplicate id: excluded, its odd status must not be counted
        row("LLR-G.1.2", "Done"),  # kept: counted
        row("LLR-G.1.3\u200b", "done"),  # unsafe id: excluded, not counted
    )
    d = derive(repo_with(tmp_path, text))
    assert sorted(p.kind for p in d.map.problems) == ["duplicate id", "unsafe id"]
    assert d.unknown_status == 1


# ------------------------------------------------------------------ the one reader, the cap


def test_canon_is_read_once_through_read_repo_text(tmp_path, monkeypatch):
    repo = repo_with(tmp_path, canon(row("HLR-F.1"), row("LLR-F.1.1")))
    reads: list[tuple[Path, int]] = []
    parses: list[int] = []
    real_read, real_parse = amod.read_repo_text, amod.parse_canon

    def read(path, cap):
        reads.append((Path(path), cap))
        return real_read(path, cap)

    def parse(text):
        parses.append(len(text))
        return real_parse(text)

    monkeypatch.setattr(amod, "read_repo_text", read)
    monkeypatch.setattr(amod, "parse_canon", parse)
    derive(repo)
    assert reads == [(repo / "REQUIREMENTS.md", LIMIT_ROLES_YML_BYTES)]
    assert len(parses) == 1


@pytest.mark.parametrize("cause", ["K1", "K2", "K3", "K4", "K5", "K6", "K7"])
def test_canon_causes(tmp_path, monkeypatch, cause):
    path = tmp_path / "REQUIREMENTS.md"
    if cause == "K1":
        path.write_text(canon(row("HLR-G.1")), encoding="utf-8")
        monkeypatch.setattr(dmod, "is_link", lambda st: True)
    elif cause == "K2":
        path.mkdir()
    elif cause == "K3":
        pass
    elif cause == "K4":
        path.write_text(canon(row("HLR-G.1")), encoding="utf-8")
        real = os.lstat

        def deny(p, *a, **k):
            if Path(p) == path:
                raise PermissionError("denied")
            return real(p, *a, **k)

        monkeypatch.setattr(os, "lstat", deny)
    elif cause == "K5":
        path.write_bytes(b"x" * (LIMIT_ROLES_YML_BYTES + 1))
    elif cause == "K6":
        path.write_bytes(b"| Id |\x00 | Status |\n")
    else:
        path.write_bytes(b"| Id | Status |\n\xff\xfe\n")
    with pytest.raises(CanonUnavailable) as err:
        derive(tmp_path)
    assert err.value.cause == CAUSE[cause]
    assert err.value.limit == LIMIT_ROLES_YML_BYTES
    assert str(err.value) == CAUSE[cause]  # the fixed text only: no path, no exception text


def test_canon_at_the_cap_loads(tmp_path):
    head = canon(row("HLR-H.1")).encode() + b"\n"
    data = head + b"x" * (LIMIT_ROLES_YML_BYTES - len(head))
    assert len(data) == LIMIT_ROLES_YML_BYTES
    assert [n.id for n in derive(repo_with(tmp_path, data)).map.nodes] == ["HLR-H.1"]


# ------------------------------------------------------------------ LLR-RMA.1.2 rule D-1


@pytest.mark.parametrize(
    "llr, candidate, present, linked",
    [
        ("LLR-Q2.1.1", "HLR-Q2.1", True, True),
        ("LLR-001.1", "HLR-001", True, True),
        ("LLR-REPAIR.1", "HLR-REPAIR", False, False),
        ("LLR-X", None, False, False),
        ("LLR-RH.6.2", "HLR-RH.6", False, False),
    ],
)
def test_rule_d1_table(tmp_path, llr, candidate, present, linked):
    rows = [row(llr)]
    if present:
        rows.insert(0, row(candidate))
    if llr == "LLR-RH.6.2":  # the candidate's row exists in the canon but cannot be parsed
        rows.insert(0, "| HLR-RH.6 | active | has | a pipe |")
    d = derive(repo_with(tmp_path, canon(*rows)))
    assert amod._candidate(llr) == candidate
    if linked:
        assert [(e.src, e.dst, e.type) for e in d.map.edges] == [(candidate, llr, "refines")]
        assert d.unlinked == ()
    else:
        assert d.map.edges == ()
        assert d.unlinked == (llr,)


def test_rule_d1_edges_are_unique_pairs_in_canon_order(tmp_path):
    d = derive(repo_with(tmp_path, canon(
        row("HLR-I.1"), row("HLR-I.2"), row("LLR-I.2.1"), row("LLR-I.1.2"), row("LLR-I.1.1"))))
    pairs = [(e.src, e.dst) for e in d.map.edges]
    assert pairs == [("HLR-I.2", "LLR-I.2.1"), ("HLR-I.1", "LLR-I.1.2"), ("HLR-I.1", "LLR-I.1.1")]
    assert len(set(pairs)) == len(pairs)


def test_an_unlinked_llr_is_never_attached_to_a_prefix(tmp_path):
    """No edge for an LLR whose own candidate is absent even when a shorter HLR prefix exists."""
    d = derive(repo_with(tmp_path, canon(row("HLR-J"), row("LLR-J.1.1"))))
    assert d.map.edges == () and d.unlinked == ("LLR-J.1.1",)


# ------------------------------------------------------------------ LLR-RMA.1.3 reported rows


def test_reported_rows_are_notes(tmp_path):
    text = canon(
        row("HLR-K.1"),
        "| LLR-K.1.1 | active | a | pipe |",
        row("LLR-K.1.2"),
        "| LLR-K.1.3 | active |",
    )
    parsed, reported = parse_canon(text)
    assert len(reported) == 2
    d = derive(repo_with(tmp_path, text))
    assert d.reported == ("unparsed row LLR-K.1.1", "unparsed row LLR-K.1.3")
    assert [n.id for n in d.map.nodes] == ["HLR-K.1", "LLR-K.1.2"]
    assert [(e.src, e.dst) for e in d.map.edges] == [("HLR-K.1", "LLR-K.1.2")]  # no guessed row
    assert d.unlinked == ()


def test_a_report_with_no_id_prints_the_generic_note(tmp_path):
    d = derive(repo_with(tmp_path, "| Id | Name |\n|---|---|\n| HLR-L.1 | x |\n"))
    assert d.reported == ("unparsed canon line",)
    assert d.map.nodes == ()


def test_unparsed_counts(tmp_path):
    """Both branches of the orphan relation (LLR-RMA.1.3), one fixture each, and a control."""
    text = canon(
        row("HLR-M.1"),  # starts-with branch: orphan LLR-M.1.1 (reported)
        row("HLR-N.1"),  # sibling-stem branch: unlinked LLR-N.1 (no HLR-N)
        row("HLR-O.1"),  # control: nothing near it
        row("LLR-O.1.1"),
        row("LLR-N.1"),
        "| LLR-M.1.1 | active | a | pipe |",
    )
    d = derive(repo_with(tmp_path, text))
    assert d.unlinked == ("LLR-N.1",)
    count = {n.id: n.unparsed for n in d.map.nodes if n.kind == "HLR"}
    assert count == {"HLR-M.1": 1, "HLR-N.1": 1, "HLR-O.1": 0}


def test_unparsed_count_of_a_dotless_hlr_is_not_doubled(tmp_path):
    """The sibling relation needs a dot in the HLR id: for `HLR-X` the starts-with branch already
    counted the reported `LLR-X.1`, and a sibling branch without the guard would count it twice."""
    text = canon(row("HLR-X"), "| LLR-X.1 | active | a | pipe |")
    d = derive(repo_with(tmp_path, text))
    assert d.reported == ("unparsed row LLR-X.1",)
    assert d.map.node("HLR-X").unparsed == 1


def test_unparsed_counts_ignore_unrelated_ids_and_hlr_rows(tmp_path):
    text = canon(row("HLR-P.1"), "| HLR-P.2 | active | a | pipe |", row("LLR-P.1.1"))
    d = derive(repo_with(tmp_path, text))
    assert d.reported == ("unparsed row HLR-P.2",)
    assert d.map.node("HLR-P.1").unparsed == 0


def test_report_line_shape_yields_id():
    """Tripwire: `parse_canon` still words a pipe-bearing row as `cannot parse row for '<id>'`;
    a rewording in derive.py fails here loudly instead of zeroing every `unparsed` count."""
    _, reported = parse_canon(canon("| LLR-Q.1.1 | active | a | pipe |"))
    assert len(reported) == 1 and "cannot parse row for 'LLR-Q.1.1'" in reported[0]
    assert amod._report_id(reported[0]) == "LLR-Q.1.1"
    _, odd = parse_canon(canon("| LLR-Q.1.2'x\\y | active | a | pipe |"))
    assert amod._report_id(odd[0]) == "LLR-Q.1.2'x\\y"
    assert amod._report_id("REQUIREMENTS.md line 3: header has no Status column") is None
    assert amod._report_id("cannot parse row for 'A' (3 cells, expected 4) and more") is None


# ------------------------------------------------------------------ LLR-RMA.1.4 read-only


def _tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        h.update(str(p.relative_to(root)).encode())
        if p.is_file():
            h.update(p.read_bytes())
    return h.hexdigest()


def test_readonly(tmp_path, monkeypatch):
    repo = repo_with(tmp_path, canon(row("HLR-R.1"), row("LLR-R.1.1")))
    (repo / "us.md").write_text("US-1\n", encoding="utf-8")
    (repo / "at.md").write_text("AT-1\n", encoding="utf-8")
    descriptor = Descriptor("reqharness", "REQUIREMENTS.md", "us.md", "at.md", ())
    before = _tree_hash(repo)
    opened: list[str] = []
    real_os_open, real_open, real_io_open = os.open, builtins.open, io.open

    def os_open(path, flags, *a, **k):
        opened.append(os.fspath(path))
        assert not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC), flags
        return real_os_open(path, flags, *a, **k)

    def py_open(file, mode="r", *a, **k):
        opened.append(os.fspath(file))
        assert set(mode) <= set("rb"), mode
        return real_open(file, mode, *a, **k)

    def io_open(file, mode="r", *a, **k):
        opened.append(os.fspath(file))
        assert set(mode) <= set("rb"), mode
        return real_io_open(file, mode, *a, **k)

    def boom(*a, **k):
        raise AssertionError("the adapter spawned a process")

    monkeypatch.setattr(os, "open", os_open)
    monkeypatch.setattr(builtins, "open", py_open)
    monkeypatch.setattr(io, "open", io_open)
    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, boom)
    monkeypatch.setattr(os, "system", boom)
    d = derive(repo, descriptor)
    assert [n.id for n in d.map.nodes] == ["HLR-R.1", "LLR-R.1.1"]
    assert opened and {Path(p).name for p in opened} == {"REQUIREMENTS.md"}  # never us.md / at.md
    monkeypatch.undo()
    assert _tree_hash(repo) == before
    assert d.map.sourced == frozenset({"HLR", "LLR"})  # configured sources do not source US/AT/TC
