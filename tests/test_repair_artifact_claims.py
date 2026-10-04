"""P-CARRY MECHANISED — an artifact's claims about disk are checked against disk.

WHY THIS EXISTS.  This batch produced the same defect THREE times: an artifact
asserting something about the tree that was not true.  A comment claiming every
caller catches `MapStoreError` (no caller does).  A comment claiming the node-id
coercion removes the phantom node (it does not).  A map correction note quoting
the falsehood it replaced, verbatim, into a scanner's input.  Each was caught by a
human reader, one at a time, at review cost.  Vigilance produced the defect three
times; a check is cheap and produces it zero times.

SCOPE, AND WHY IT IS NARROW.  Only two claim shapes are mechanised, because only
two are unambiguously decidable:

  1. a `path:line` citation must resolve to a real file with that many lines;
  2. a `test_*` identifier cited as a node must exist among collected nodes.

CORPUS: this batch's authored artifacts AND `mapper/` source.  The source half was
added at close-out, because three of the four recorded instances were COMMENTS,
not artifact lines -- a checker reading only `.dev-flow/` could not see the place
the defect actually lives.

Prose claims ("every caller catches X") are NOT checked -- deciding those needs
the semantics of the claim, and a checker that guesses would false-fail correct
work, which costs as much as passing wrong work (C-53).

AND THE BOUNDARY IS NOW KNOWN TO BE LOAD-BEARING, not theoretical.  The batch's
close-out raised a fifth instance -- a disposition row recording a control as
"gated by `Q-high1`: 8 arms" when four mutants that break two of its three limbs
left all 548 arms green.  NO TEXT CHECKER CAN DECIDE THAT: "X is gated" is a claim
about what a mutation does, and settling it requires RUNNING the mutation.  The
mechanical guard for that class is not here; it is at the product level, in the
per-limb arms and the totality assertion `test_at_p02i`.  Saying so explicitly is
the point -- a checker that appears to cover a class it cannot decide is worse
than one whose limits are written down.

THIS FILE'S OWN CHECKER FALSE-FAILED TWICE BEFORE IT WORKED, which is the reason
the resolution rules below are as fussy as they are:
  * a bare basename (`store.py`) is not a path -- it must be resolved, or 65
    correct citations read as missing files;
  * a basename can be AMBIGUOUS across batch directories -- resolving to the
    first match reported 6 valid citations as past-EOF, because it picked a
    different batch's `increment-001.md`;
  * most cited test names are STEMS of parametrized node ids, or module names.
A probe is code, and it needs verifying like any other (C-55's rider).

REVIEW ARTIFACTS ARE EXCLUDED, DELIBERATELY.  `0*-review`/`0*-qa-*`/`0*-security-*`
are written by independent reviewers.  They are evidence authored by someone else;
editing them to satisfy a check would corrupt the record this batch is judged on.
Their claims are the reviewer's to stand behind, not mine to rewrite.
"""
from __future__ import annotations

import functools
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
BATCH = REPO / ".dev-flow" / "2026-08-27-repair-batch-02"

_CITATION = re.compile(r"`([A-Za-z0-9_./\\-]+\.(?:py|md|json)):(\d+)(?:-(\d+))?`")
_TEST_NAME = re.compile(r"\b(test_[a-z0-9_]{6,})\b")


def _authored() -> list[Path]:
    """This batch's OWN artifacts -- reviewer-authored evidence excluded."""
    return sorted(
        p
        for p in BATCH.rglob("*.md")
        if not re.match(r"^0\d[a-z]?-(review|qa|security)", p.name)
        and "code-review" not in p.name
    )


def _source() -> list[Path]:
    """Product source -- because `mapper/` carries claims and was not being read.

    HONEST SCOPE, corrected after the re-confirmation review MEASURED what this
    widening buys.  The three `mapper/` instances that motivated it were all PROSE
    claims ("every caller catches X", "the coercion removes the phantom node",
    "extends any round-tripped dataclass"), and the two rules below decide
    `path:line` and `test_*` citations ONLY -- so the widening catches **none of
    them**, including the over-claim an earlier draft of this very docstring made.
    What it does buy is real and small: `mapper/` carries 4 checkable citations
    across 2 of its 33 files, and those are now checked instead of unread.  Saying
    it buys more would be the same over-claim this file exists to catch.

    Verified non-false-failing before landing (C-53: run a new rule over a corpus
    you believe is CORRECT): the four citations `mapper/` carries today all resolve
    -- `app.py:450` and `app.py:1179` against a 2072-line file, `test_keymap` to a
    module, `test_at_p02i` to a collected node -- and both basenames are unambiguous.
    """
    return sorted((REPO / "mapper").rglob("*.py"))


def _corpus() -> list[Path]:
    return _authored() + _source()


def _resolve(cited: str, citing: Path) -> Path | None:
    """Resolve a citation to one file, or `None` when it is ambiguous/absent.

    Ambiguity is resolved toward the CITING artifact's own directory tree first:
    three batches each own an `increment-001.md`, and picking the wrong one turns
    valid citations into false violations.
    """
    direct = REPO / cited
    if direct.exists():
        return direct
    name = Path(cited).name
    hits = [
        p
        for p in REPO.rglob(name)
        if ".git" not in p.parts and "__pycache__" not in p.parts
    ]
    if not hits:
        return None
    local = [p for p in hits if BATCH in p.parents]
    if len(local) == 1:
        return local[0]
    return hits[0] if len(hits) == 1 else None


@functools.lru_cache(maxsize=1)
def _live_nodes() -> set[str]:
    """Collected node names.  CACHED: the widened corpus made this 41 arms,
    and an uncached collection subprocess per arm added minutes to the suite
    for an answer that cannot change within a run.
    """
    out = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--collect-only",
         "-p", "no:randomly", "-o", "addopts="],
        cwd=REPO, capture_output=True, text=True,
    ).stdout
    return set(re.findall(r"::(test_[A-Za-z0-9_]+)", out))


def test_the_checker_can_see_its_corpus():
    """A probe returning zero because it looked nowhere is not a clean result.

    C-55's rider: an absence is admissible only if the probe that produced it can
    produce a NON-absence.  Both arms below report violations by finding none, so
    the corpus and the live-node set must be asserted non-degenerate first.
    """
    artifacts = _authored()
    assert len(artifacts) >= 5, f"only {len(artifacts)} authored artifacts found"
    text = "\n".join(a.read_text(encoding="utf-8") for a in artifacts)
    # MEASURED, not guessed: the authored set carries 10 such citations today.
    # (It read 8, correct at `01d7578` and stale from the next commit on -- this
    # comment is itself the decay it warns about.)
    # The floor exists to catch the regex silently ceasing to match, not to
    # mandate a citation count -- a predicted threshold false-fails correct work
    # (C-39), and the first draft of this line said 10 and did exactly that.
    assert len(_CITATION.findall(text)) >= 5, "no path:line citations parsed"
    assert len(_TEST_NAME.findall(text)) >= 10, "no test identifiers parsed"


def test_the_flow_state_file_parses():
    """`.dev-flow/state.json` is what the NEXT session reads to orient itself.

    An unparseable one asserts nothing at all, which is the C-44 shape this
    project keeps naming -- work that looks recorded and is not.  Added after a
    missing comma shipped in a commit: the file was edited by hand, the edit was
    not re-parsed, and nothing in the suite could contradict it.

    Asserts the shape the flow actually reads, not merely that the bytes are
    JSON, so a file that parses while having lost its batch identity still
    reddens.
    """
    import json

    state = REPO / ".dev-flow" / "state.json"
    assert state.exists(), "the flow state file is gone"
    data = json.loads(state.read_text(encoding="utf-8"))
    for key in ("project", "batch_id", "current_station", "phase_status"):
        assert key in data, f"state.json lost its {key!r} key"
    # The SOURCE half of the corpus needs its own floor, and this is the one that
    # was missing: `mapper/` is where three of the four false claims actually
    # lived.  Without it, a rename could reduce the widened corpus to nothing and
    # both arms below would go on passing by looking nowhere -- the emptiness
    # doing work, silently (C-55 limb 1).  Measured today: 2 of each.
    src = _source()
    assert len(src) >= 3, f"only {len(src)} source files found"
    src_text = "\n".join(p.read_text(encoding="utf-8") for p in src)
    assert len(_CITATION.findall(src_text)) >= 1, "no path:line citation in mapper/"
    assert len(_TEST_NAME.findall(src_text)) >= 1, "no test identifier in mapper/"
    nodes = _live_nodes()
    assert len(nodes) >= 200, f"collected only {len(nodes)} nodes; collection broke"


@pytest.mark.parametrize("artifact", _corpus(), ids=lambda p: p.name)
def test_every_path_line_citation_resolves(artifact):
    """A `file.py:NNN` citation must name a real file with at least NNN lines."""
    bad = []
    for match in _CITATION.finditer(artifact.read_text(encoding="utf-8")):
        cited = match.group(1)
        last = int(match.group(3) or match.group(2))
        target = _resolve(cited, artifact)
        if target is None:
            bad.append(f"{cited}: unresolvable or ambiguous")
            continue
        length = len(target.read_text(encoding="utf-8", errors="replace").splitlines())
        if last > length:
            bad.append(f"{cited}:{last} but {target.name} has {length} lines")
    assert not bad, f"{artifact.name} cites what disk does not have: {bad}"


@pytest.mark.parametrize("artifact", _corpus(), ids=lambda p: p.name)
def test_every_cited_test_identifier_exists(artifact):
    """A cited `test_*` must be a collected node, or the stem of one.

    Catches the class an independent QA pass found by hand: three node citations
    naming tests that do not exist, one of them inside the disposition row of a
    finding about false records.
    """
    modules = {p.stem for p in (REPO / "tests").glob("*.py")}
    nodes = _live_nodes()
    cited = set(_TEST_NAME.findall(artifact.read_text(encoding="utf-8")))
    phantom = sorted(
        c
        for c in cited
        if c not in modules
        and not any(n == c or n.startswith(c) for n in nodes)
    )
    assert not phantom, (
        f"{artifact.name} cites test nodes that do not exist on disk: {phantom}"
    )
