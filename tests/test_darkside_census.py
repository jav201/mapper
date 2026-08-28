"""The hue census — HLR-S06.1, HLR-S06.2, HLR-S06.3 and LLR-COERCE.1.

The value of S-6 is not the three hexes; it is that a later batch cannot quietly
reuse a hue for a second meaning.  Only a TOTALITY clause evaluated at gate time
can catch the site a later batch adds, so the census derives its input set from
the tracked tree and fails on any derived site no one has classified.

Register key.  A row is keyed by (path, stripped source line), never by line
NUMBER: addresses move on every unrelated edit -- this batch alone moved the
blue literals from app.py:1864 to :1920 and the ACCENT definition from
darkside.py:17 to :51 -- and a census that reddens when a line merely MOVES is a
false-failure generator, which costs as much as one that passes wrong work.
Keyed on the line's text, moving a site is silent, EDITING one forces it to be
re-judged, and ADDING one reddens until someone classifies it.

Split of labour (the reason the method is honestly `test (unit)`): assigning a
job to a site is a human judgement, made once by reading the line and written
down below; the test asserts totality and job-equality mechanically.
"""
import itertools
import math
import re
import subprocess
import unicodedata
from pathlib import Path

import pytest
from rich.color import EIGHT_BIT_PALETTE, Color, ColorSystem

from mapper import darkside

REPO = Path(__file__).resolve().parents[1]

ADJUDICATED_TOKENS = ("ACCENT", "WARN", "ALERT", "PULSE")


def declared_jobs() -> dict[str, str]:
    """Every token's job, PARSED FROM THE PRODUCT's own docstring.

    Not re-typed here.  A second copy would agree on the day it was written and
    drift the first time one was edited -- and worse, it would make the one-job
    census detect only edits to ITSELF: giving two tokens the same job in
    `darkside.__doc__` would redden nothing, because the table under test would
    be independent of the product.  That is the defect the coercion clauses
    forbid one file over, and it has to hold here too.

    The longest name is tried first, so a token whose name is a prefix of
    another cannot shadow it, and the terminating lookahead requires a NAME
    after the two spaces rather than merely two spaces -- so a job line may
    wrap.  The lookahead also terminates on a line at column 0: without it the
    LAST declared token swallows the whole trailing paragraph, which measured
    423 characters against a real job of 21.  That was harmless only because
    the over-captured token was not one of the adjudicated four, and it stops
    being harmless the moment the equality below quantifies over all of them.
    """
    names = "|".join(sorted(darkside.tokens(), key=len, reverse=True))
    body = re.findall(
        rf"^\s{{2}}({names})\s+(.*?)(?=^\s{{2}}(?:{names})\s|^\S|\Z)",
        darkside.__doc__, re.M | re.S,
    )
    return {name: " ".join(job.split()) for name, job in body}


TOKEN_JOB = {n: j for n, j in declared_jobs().items() if n in ADJUDICATED_TOKENS}


# --------------------------------------------------------------------------
# LLR-S06.3.1 — the census derives its own input set


def tracked_sources() -> dict[str, str]:
    """`git ls-files` over mapper/, not rglob and not glob.

    The three agree today at 33 files and stop agreeing the moment an untracked
    or ignored .py lands under mapper/; the census is over TRACKED product
    source, and saying so in the command is what keeps that true.  The
    non-recursive `glob.glob('mapper/*.py')` yields 16 -- a plausible weaker
    commit that loses half the tree.
    """
    out = subprocess.run(
        ["git", "ls-files", "mapper/*.py", "mapper/**/*.py"],
        cwd=REPO, capture_output=True, text=True, check=True,
    )
    return {p: (REPO / p).read_text(encoding="utf-8") for p in out.stdout.split()}


def test_llr_s06_3_1_the_derived_file_set_equals_the_tracked_tree():
    """Asserted as a SET, not against a floor.

    A `>= 30` bound does catch the 16-file non-recursive glob, but only by the
    accident of the gap: a derivation that lost three files, or gained a module
    and lost four, sits comfortably above the floor and ships a census with
    holes.  Naming the command and asserting the set removes the dependence on
    how large the loss happens to be.
    """
    derived = set(tracked_sources())
    rglob = {
        p.relative_to(REPO).as_posix()
        for p in (REPO / "mapper").rglob("*.py")
        if "__pycache__" not in p.parts
    }
    assert derived == rglob
    assert derived, "the derived input set is empty: every clause over it is vacuous"


def test_llr_s06_3_1_an_emptied_input_set_reddens_rather_than_passing():
    """The mutation arm: a census that passes on empty input is not a census."""
    with pytest.raises(AssertionError):
        _assert_hue_set_is_exactly_the_declared_tokens({})


# --------------------------------------------------------------------------
# The derivations


# 6 OR 8 digits.  An 8-digit literal carries an alpha channel and is plausible
# exactly where 6 of the 8 blue literals already live -- the Textual CSS blocks.
#
# Both earlier forms were blind to it, for the same reason: `{6}\b` and
# `{6}(?![0-9a-fA-F])` each fail on an alpha-suffixed literal because the 7th
# character IS a hex digit, so nothing matches and there is no second `#` to
# restart from.  Swapping the `\b` for the lookahead changed only the behaviour
# against NON-hex word characters, which was never the complaint; it was
# reported as a fix and repaired nothing.  An 8-digit hue is reported at full
# length so it reads as UNDECLARED rather than being silently normalised into a
# declared token.
HEX = re.compile(r"#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?(?![0-9a-fA-F])")
ADJUDICATED = re.compile(r"\bdarkside\.(WARN|ALERT|PULSE)\b")
BLUE = re.compile(re.escape(darkside.ACCENT), re.IGNORECASE)


def _sites(sources, pattern):
    """(path, stripped line, sorted tokens) for every line the pattern matches."""
    found = []
    for path, blob in sorted(sources.items()):
        for line in blob.splitlines():
            hits = pattern.findall(line)
            if hits:
                found.append((path, line.strip(), tuple(sorted(set(hits)))))
    return found


def test_hex_can_see_an_alpha_suffixed_literal():
    """The control the finding asked for, and the reason it asked.

    `test_hue_census_no_undeclared_hue_ships` is the clause that found the
    undeclared grey.  A pattern that cannot SEE a literal reports no match and
    no failure, which is indistinguishable from a clean tree.
    """
    assert HEX.findall("color: #1783ffcc;") == ["#1783ffcc"]
    assert HEX.findall("background: #1783ff;") == ["#1783ff"]
    assert HEX.findall("#1783ffzz") == ["#1783ff"]
    assert HEX.findall("#12345") == []


def _assert_hue_set_is_exactly_the_declared_tokens(sources):
    hues = {m.lower() for blob in sources.values() for m in HEX.findall(blob)}
    assert hues, "no hue literal was derived: this clause would pass vacuously"
    declared = {v.lower() for v in darkside.tone_set()}
    assert hues == declared, (
        f"undeclared hues ship: {sorted(hues - declared)}; "
        f"declared but unused: {sorted(declared - hues)}"
    )


# --------------------------------------------------------------------------
# The register — one row per derived site, judged once by reading the line.
#
# CONFORMING means: a human read this line and confirmed the site expresses its
# token's single declared job.  A site absent from both this set and the
# exception register below is a FAILURE, not a skip.

CONFORMING_SEVERITY = {
    ("mapper/app.py", "number_style = darkside.INK if sin_acta == 0 and vencen == 0 else darkside.WARN"),
    ("mapper/app.py", 'lines.append(f"▲ {vencen} vencen hoy", darkside.WARN)'),
    ("mapper/app.py", '("sin acta ", darkside.WARN), (f"{sin} ", darkside.WARN),'),
    ("mapper/app.py", 'darkside.microbar(sin, total, fill=darkside.WARN), ("    ", ""),'),
    ("mapper/app.py", 'text.append(f"{marker} {stage}", darkside.PULSE if self.loading else darkside.INK)'),
    ("mapper/app.py", 'return Text.assemble(("● ", darkside.ALERT), ("bloqueado", darkside.ALERT))'),
    ("mapper/app.py", 'return Text.assemble(("● ", darkside.WARN), ("riesgo", darkside.WARN))'),
    ("mapper/app.py", 'return ("░", darkside.WARN)'),
    ("mapper/app.py", '("░", darkside.WARN), (" baja ", darkside.MUT),'),
    ("mapper/screens/coverage.py", 'Text.assemble((escape(",".join(missing)), darkside.ALERT)),'),
    ("mapper/screens/factory.py", '("no se puede dibujar: el mapa tiene un ciclo", darkside.ALERT)'),
    ("mapper/screens/factory.py", 'return Text.assemble(("archivo de plantilla no encontrado", darkside.ALERT))'),
    ("mapper/screens/factory.py", 'parts.append((escape(f"{{{{{key}}}}}"), darkside.ALERT))'),
    ("mapper/views/lane.py", '"risk": darkside.WARN,'),
    ("mapper/views/lane.py", '"late": darkside.WARN,'),
    ("mapper/views/lane.py", '"blocked": darkside.ALERT,'),
    # The branch is `if state == "pending"` (lane.py:66): the CI state is
    # literally PENDING, which is WARN's declared job verbatim.  Only the LABEL
    # says " run".  Registered as an exception in the first draft of this file
    # by reading the label instead of the condition -- corrected here.
    ("mapper/views/lane.py", 'return Text.assemble(("◐", darkside.WARN), (" run", darkside.WARN))'),
    ("mapper/views/lane.py", 'return Text.assemble(("●", darkside.ALERT), (" fail", darkside.ALERT))'),
    ("mapper/views/layered.py", '"risk": darkside.WARN,'),
    ("mapper/views/layered.py", '"late": darkside.WARN,'),
    ("mapper/views/layered.py", '"blocked": darkside.ALERT,'),
    ("mapper/views/layered.py", "style=darkside.WARN,"),
    ("mapper/views/layered.py", 'cv.put(chip_x + j, y, ch, f"{darkside.GROUND} on {darkside.WARN}")'),
    ("mapper/views/layered.py", "doc_style = darkside.INK if doc else darkside.ALERT"),
    # Inc-3 / HLR-N06.2 — the fold pill's left bar and its hit count.  Judged by
    # reading the lines: `LLR-S06.3.5` gives WARN the single job "outstanding
    # attention -- work pending, due, at risk or in flight, and nothing has
    # failed", and a folded branch is a branch whose contents the operator still
    # has to come back to; the numeral beside it counts query matches sealed
    # inside it, which is pending work with a quantity.  Nothing has failed, so
    # ALERT would be the wrong token, and the requirement's own corrected reason
    # (§6.5 A-10, which struck "WARN is correct because it means a hit") is the
    # one applied here.
    ("mapper/views/layered.py", 'cv.put(cx, y + card_h, "▐", darkside.WARN)'),
    ("mapper/views/layered.py", "cv.text(cx + 2 + len(core), y + card_h, tail, darkside.WARN)"),
    ("mapper/views/outline.py", "style=darkside.WARN,"),
    ("mapper/views/outline.py", "style = darkside.WARN if missing else darkside.MUT"),
    ("mapper/views/radial.py", "style=darkside.WARN,"),
    ("mapper/widgets/inspector.py", "(darkside.plain(text), darkside.ALERT),"),
    ("mapper/widgets/inspector.py", '("  requerido", darkside.ALERT),'),
    ("mapper/widgets/rail.py", "darkside.ALERT,"),
    ("mapper/widgets/rail.py", 'parts.append((f"{missing:>3}", darkside.WARN))'),
}

CONFORMING_BLUE = {
    ("mapper/app.py", "background: #1783ff;"),
    ("mapper/app.py", "#map-inspector Input:focus { background: #1783ff; color: #000000; }"),
    ("mapper/app.py", "#template-table > .datatable--cursor { background: #1783ff; color: #000000; }"),
    ("mapper/darkside.py", 'ACCENT = "#1783ff"'),
    ("mapper/screens/coverage.py", "background: #1783ff;"),
    ("mapper/screens/factory.py", "background: #1783ff;"),
    ("mapper/screens/palette.py", "background: #1783ff;"),
}

# Known-open exceptions.  Each names the increment that closes it, so the
# stale-exception guard below reddens if that increment forgets -- a mechanical
# handoff instead of a promise.
OPEN_EXCEPTIONS = {
    ("mapper/screens/factory.py", ".factory-tag { color: #1783ff; }"):
        "ACCENT on a non-interactive tag. A tag is a label, not an affordance "
        "(the sibling .factory-node-selected at :101 uses the same blue as a "
        "selection background, which IS legitimate). Retones to MUT in Inc-9, "
        "which owns screens/factory.py.",
    ("mapper/views/lane.py",
     'parts.append(("▱", darkside.ALERT if behind else darkside.STEP))'):
        "Being N commits BEHIND is neither a failure nor a blockage -- it is "
        "work pending or at risk, which is WARN's job. The same file already "
        "paints '\"late\": darkside.WARN' for the same concept, so the two "
        "contradict each other. Retones to WARN in Inc-5, which owns lane.py.",
    ("mapper/views/lane.py",
     'return Text.assemble(("-", darkside.ALERT), (str(behind), darkside.ALERT), (" ", ""), blocks)'):
        "The behind-chip, same concept and same file as the row above. "
        "Retones to WARN in Inc-5.",
    ("mapper/views/layered.py",
     'cv.text(gx, gy + 2, "~" + ghost[:-1], darkside.ALERT)'):
        "A removed node rendered as an 'alert ghost'. A node that is GONE is "
        "absent information, which the palette assigns to MUT; it is not an "
        "item that cannot proceed. Retones to MUT in Inc-3, which owns "
        "views/layered.py.",
    ("mapper/views/lane.py", 'text.append("▱", style=darkside.ALERT)'):
        "_mini_timeline's BEHIND slot -- the same concept as the two rows "
        "above, two functions away in the same file, and worse: total is "
        "max(1, ahead + behind), so it paints one ALERT block even when behind "
        "is 0. Registering the other two and not this one would leave the "
        "register with no oracle for the concept. Retones to WARN in Inc-5.",
    ("mapper/app.py", "style=darkside.INK if doc else darkside.ALERT)"):
        "'sin acta' painted ALERT here and WARN at the dashboard hero row "
        "(app.py 'sin acta ', darkside.WARN). The same literal string and the "
        "same concept in two severity tokens, both previously CONFORMING. "
        "Under the amended jobs a ficha lacking its acta is work PENDING, not "
        "an item that cannot proceed. Retones to WARN in Inc-7, which owns "
        "app.py for the sala.",
}


# --------------------------------------------------------------------------
# HLR-S06.3 / LLR-S06.3.4 / LLR-S06.3.5 — the census itself


def test_hue_census_no_undeclared_hue_ships():
    """M-3 found `#a3a3a3` at views/radial.py:18, a member of no token set.

    A census over a list of hues someone typed cannot detect the hue nobody
    typed; this one derives its input from the tree, which is how that site was
    found in the first place.
    """
    _assert_hue_set_is_exactly_the_declared_tokens(tracked_sources())


def test_hue_census_every_severity_and_busy_site_is_classified():
    """TOTALITY: a derived site with no register row is a failure, not a skip."""
    sites = _sites(tracked_sources(), ADJUDICATED)
    # 36 -> 38 in Inc-3: the fold pill's WARN bar and its WARN hit count, both
    # judged and registered in CONFORMING_SEVERITY above.
    assert len(sites) == 38, f"derived {len(sites)} severity/busy lines, expected 38"

    unclassified = [
        (path, line) for path, line, _ in sites
        if (path, line) not in CONFORMING_SEVERITY
        and (path, line) not in OPEN_EXCEPTIONS
    ]
    assert unclassified == []


def test_hue_census_no_blue_LITERAL_ships_outside_an_interactive_site():
    """LLR-S06.3.3, quantified over the derived LITERAL set — 8 sites.

    NOT over the 42 symbolic `darkside.ACCENT` references, and the name says so.
    The scope is the sealed requirement's own: `LLR-S06.3.3`'s Touched-symbols
    line enumerates the eight `#1783ff` literal sites and quantifies over those.
    So this test matches its requirement — but "the blue stays interactivity
    only" is a claim about the whole surface, and 8 of 50 sites does not
    establish it.  Widening the derivation to the symbolic form is a REQUIREMENT
    gap, carried as `B-43` with an owning increment, not an implementation gap
    to be papered over with a broader test name than the test earns.
    """
    sites = _sites(tracked_sources(), BLUE)
    assert len(sites) == 8, f"derived {len(sites)} blue literal lines, expected 8"

    unclassified = [
        (path, line) for path, line, _ in sites
        if (path, line) not in CONFORMING_BLUE
        and (path, line) not in OPEN_EXCEPTIONS
    ]
    assert unclassified == []


def test_llr_s06_3_5_no_site_classifies_as_both_jobs_and_none_as_neither():
    """The clause that reddens `M-S06.3.5-a`.

    Declaring the job of both severity tokens as "severity" would classify all
    36 sites and make the two interchangeable -- which is the defect, not the
    fix, because a single shared job makes every site classify as BOTH.
    """
    jobs = set(TOKEN_JOB.values())
    assert len(jobs) == len(TOKEN_JOB), "two tokens share a job: the census has no oracle"

    for path, line, tokens in _sites(tracked_sources(), ADJUDICATED):
        if (path, line) in OPEN_EXCEPTIONS:
            continue
        site_jobs = {TOKEN_JOB[t] for t in tokens}
        assert len(site_jobs) == 1, f"{path} classifies as both: {sorted(site_jobs)} -- {line}"


def test_llr_s06_3_2_every_registered_exception_still_exists():
    """A stale entry fails, so the register cannot silently license a third site."""
    sources = tracked_sources()
    for (path, line), reason in OPEN_EXCEPTIONS.items():
        assert path in sources, f"registered exception names a file that is gone: {path}"
        present = {ln.strip() for ln in sources[path].splitlines()}
        assert line in present, f"stale exception, no longer in {path}: {line}"
        assert reason.strip()


def test_llr_s06_3_2_the_register_is_the_size_the_dispositions_imply():
    """Derived from the dispositions, not typed.

    After Inc-1: six.  `#D10`'s ruling promotes radial.py's `#a3a3a3` to a token
    and retones the progress site, so neither is registered.  What stays is
    factory.py's tag (`#D10`'s own entry, Inc-9) plus five sites the census
    surfaced by being derived rather than hand-listed: three ALERT-for-behind
    uses in lane.py (Inc-5), layered.py's removed-node ghost (Inc-3), and the
    'sin acta' string painted in two different severity tokens (Inc-7).

    After Inc-3: five.  After Inc-5: two.  After Inc-7: one.  After Inc-9: zero.
    """
    assert len(OPEN_EXCEPTIONS) == 6
    owners = {"Inc-3", "Inc-5", "Inc-7", "Inc-9"}
    for reason in OPEN_EXCEPTIONS.values():
        assert any(o in reason for o in owners), (
            "every registered exception names the increment that closes it, or "
            "the handoff is a promise rather than a mechanism"
        )


# --------------------------------------------------------------------------
# HLR-S06.1 — the tokens and their jobs
# AT-003


def test_at_003_the_three_v2_tokens_carry_their_exact_values():
    assert darkside.SAGE == "#2fbf71"
    assert darkside.TEAL == "#22b8cf"
    assert darkside.VIOLET == "#9775fa"


def test_at_003_no_two_tokens_declare_the_same_job():
    """The one-job rule, quantified over ALL 14 tokens — not the adjudicated 4.

    `mapper/darkside.py` opens by asserting "Every colour token carries EXACTLY
    ONE job", and until this existed the census checked that claim over four of
    them.  Giving two of the other ten the same job line in the PRODUCT reddened
    nothing, while the docstring asserting the universal was itself pinned.
    """
    jobs = declared_jobs()
    assert set(jobs) == set(darkside.tokens()), (
        f"a declared token has no job line: {sorted(set(darkside.tokens()) - set(jobs))}"
    )
    collisions = {j for j in jobs.values() if list(jobs.values()).count(j) > 1}
    assert collisions == set(), f"two tokens share a job: {sorted(collisions)}"


def test_at_003_no_job_swallows_the_prose_that_follows_it():
    """The last declared token terminates at the paragraph, not at the file.

    Measured before the terminator was added: the final token's parsed job ran
    to 423 characters against a real job of 21, because its alternative ended at
    `\\Z`.  A parser that silently returns a partial-quality dict makes the
    census above look stronger while being weaker.

    The oracle is the trailing paragraph's own text, not a LENGTH BOUND.  A
    bound is a proxy: `ASH`'s job is legitimately 162 characters over three
    wrapped lines, so `< 120` false-failed a correct parse -- which costs as
    much as passing a wrong one.
    """
    jobs = declared_jobs()
    assert jobs["VIOLET"] == "relaciones / enlaces."

    # The prose that follows the token block, and which the last token used to
    # swallow whole.  Any job containing it has over-captured.
    tail_marker = "deliberately does NOT read"
    assert tail_marker in darkside.__doc__, "the fixture for this test is gone"
    leaked = {n: j for n, j in jobs.items() if tail_marker in j}
    assert leaked == {}, f"a job swallowed the trailing prose: {sorted(leaked)}"


def test_at_003_every_token_states_its_job_in_the_module_docstring():
    """The value of this story is the docstring, not the hex.

    Three hues with no declared job is decoration; three hues with declared
    jobs is a contract a later batch can be held to.
    """
    doc = darkside.__doc__
    assert doc
    for name in darkside.tokens():
        assert re.search(rf"^\s{{2}}{name}\s", doc, re.M), f"{name} has no job line"
    assert "EXACTLY ONE job" in doc


def test_at_003_warn_does_not_claim_work_that_is_merely_in_flight():
    """The narrowing that keeps `sites classifying as both == 0` satisfiable.

    With `or in flight` still in WARN's job, the loading ladder's in-progress
    rung classifies under WARN *and* PULSE at once, and LLR-S06.3.5's own
    threshold cannot be met by any implementation.

    An earlier version of this docstring also named lane.py's CI chip as such a
    site.  It is NOT one: that branch is `state == "pending"`, and pending is
    WARN's job verbatim, so the chip is registered CONFORMING above.  Its
    defect is that its label and glyph both say *running* for a state that is
    *pending* -- copy and glyph, not hue (carry `B-38`).  Naming it here as
    in-flight work contradicted the register 180 lines up.
    """
    warn_job = re.search(r"^\s{2}WARN\s+(.*?)(?=^\s{2}ALERT)", darkside.__doc__,
                         re.M | re.S).group(1)
    assert "in flight" not in warn_job
    assert "pending, due, or at risk" in " ".join(warn_job.split())


# --------------------------------------------------------------------------
# HLR-S06.2 — the tokens survive the 256-colour downgrade
# AT-004


def slot(value: str) -> int:
    """A FRESH Color per call.

    `Style.parse` is LRU-cached and caches `_ansi`, so a downgrade probe that
    reuses a Style silently returns the FIRST rung's codes for every later rung
    -- reporting "no collisions" at every rung.  Measured; the lens's own first
    attempt was contaminated this way.
    """
    return Color.parse(value).downgrade(ColorSystem.EIGHT_BIT).number


def test_at_004_the_three_new_tokens_hold_three_distinct_free_slots():
    new = {n: slot(getattr(darkside, n)) for n in ("SAGE", "TEAL", "VIOLET")}
    assert set(new.values()) == {35, 38, 105}
    shipped = {
        slot(v) for n, v in darkside.tokens().items()
        if n not in ("SAGE", "TEAL", "VIOLET")
    }
    assert not (set(new.values()) & shipped)


def test_at_004_no_two_declared_tokens_collapse_onto_one_slot():
    slots = {}
    for name, value in darkside.tokens().items():
        slots.setdefault(slot(value), []).append(name)
    collisions = {s: n for s, n in slots.items() if len(n) > 1}
    assert collisions == {}


def _lab(value: str) -> tuple[float, float, float]:
    r, g, b = (int(value[i:i + 2], 16) / 255 for i in (1, 3, 5))
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
    r, g, b = lin
    xyz = (
        (r * 0.4124564 + g * 0.3575761 + b * 0.1804375) / 0.95047,
        (r * 0.2126729 + g * 0.7151522 + b * 0.0721750),
        (r * 0.0193339 + g * 0.1191920 + b * 0.9503041) / 1.08883,
    )
    f = [t ** (1 / 3) if t > 216 / 24389 else (841 / 108) * t + 4 / 29 for t in xyz]
    return (116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2]))


def _ciede2000(lab1, lab2) -> float:
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2)
    Cbar = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cbar ** 7 / (Cbar ** 7 + 25 ** 7))) if Cbar else 0.5
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360 if (a1p or b1) else 0.0
    h2p = math.degrees(math.atan2(b2, a2p)) % 360 if (a2p or b2) else 0.0
    dLp, dCp = L2 - L1, C2p - C1p
    if C1p * C2p == 0:
        dhp = 0.0
    elif abs(h2p - h1p) <= 180:
        dhp = h2p - h1p
    else:
        dhp = h2p - h1p - math.copysign(360, h2p - h1p)
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp) / 2)
    Lbp, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    if C1p * C2p == 0:
        hbp = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hbp = (h1p + h2p) / 2
    elif h1p + h2p < 360:
        hbp = (h1p + h2p + 360) / 2
    else:
        hbp = (h1p + h2p - 360) / 2
    T = (1 - 0.17 * math.cos(math.radians(hbp - 30))
         + 0.24 * math.cos(math.radians(2 * hbp))
         + 0.32 * math.cos(math.radians(3 * hbp + 6))
         - 0.20 * math.cos(math.radians(4 * hbp - 63)))
    Sl = 1 + (0.015 * (Lbp - 50) ** 2) / math.sqrt(20 + (Lbp - 50) ** 2)
    Sc, Sh = 1 + 0.045 * Cbp, 1 + 0.015 * Cbp * T
    Rt = (-math.sin(math.radians(2 * (30 * math.exp(-(((hbp - 275) / 25) ** 2)))))
          * (2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7)) if Cbp else 0.0))
    return math.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2
                     + Rt * (dCp / Sc) * (dHp / Sh))


def _rendered(value: str) -> str:
    return "#%02x%02x%02x" % EIGHT_BIT_PALETTE[slot(value)]


def test_at_004_the_semantic_tokens_clear_the_perceptual_floor():
    """>= 10 CIEDE2000 at the GUARANTEED rung, over pairs derived from the set.

    Quantified over the SEMANTIC tokens: including the surfaces measures the
    GROUND/PANEL distance (3.20), which is a property of the page and not of
    the palette.  Measured floor is 13.99 at ACCENT/VIOLET -- roughly six times
    the ~2.3 just-noticeable difference.
    """
    semantic = darkside.semantic_tokens()
    assert len(semantic) >= 10, "the derived semantic set shrank; the floor is over fewer pairs"
    worst = min(
        (_ciede2000(_lab(_rendered(semantic[a])), _lab(_rendered(semantic[b]))), a, b)
        for a, b in itertools.combinations(sorted(semantic), 2)
    )
    assert worst[0] >= 10, f"{worst[1]}/{worst[2]} are {worst[0]:.2f} apart"


def test_at_004_surfaces_and_semantics_separate_by_luminance():
    """The class boundary is DECLARED, so it needs a guard that reddens a
    mis-filed future token rather than silently moving the floor."""
    def lum(value):
        r, g, b = (int(value[i:i + 2], 16) / 255 for i in (1, 3, 5))
        lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
               for c in (r, g, b)]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

    surfaces = [lum(v) for v in darkside.SURFACES]
    semantic = [lum(v) for v in darkside.semantic_tokens().values()]
    assert surfaces and semantic
    assert max(surfaces) < 0.10 < min(semantic)


# --------------------------------------------------------------------------
# LLR-COERCE.1 — the range list is declared once, and the map covers it


def test_llr_coerce_1_no_declared_code_point_survives_plain():
    """The threshold is over `plain()`'s BEHAVIOUR, not the constant's existence.

    `M-COERCE.1-a` -- declare COERCION_RANGES and leave _CONTROL_MAP as shipped
    -- makes the constant exist and every reference resolve, while 22 code
    points still pass through untouched, every bidi range among them.
    """
    points = [cp for lo, hi in darkside.COERCION_RANGES for cp in range(lo, hi + 1)]
    assert len(points) == len(set(points)), "the declared ranges overlap"
    assert points, "the declared list is empty: the survivor count is vacuously 0"
    survivors = [cp for cp in points if darkside.plain(chr(cp)) == chr(cp)]
    assert survivors == []


def test_llr_coerce_1_the_declared_list_equals_its_unicode_classes():
    """THE INDEPENDENT ORACLE. Everything else here is derived from the list.

    Every other coercion clause reads `COERCION_RANGES` and therefore cannot
    detect that the list is SHORT -- it can only detect that the list is not
    applied.  Measured twice: a row labelled "C0 except TAB and LF" omitted
    U+000D and its own count said 29 where the label implies 30; a row labelled
    "zero-width and invisible" stopped one code point short of the invisible
    operators, leaving 19 invisible points reaching the exported SVG while the
    suite was green.  Neither is reachable from an oracle built out of the list.

    `unicodedata` is the oracle because it is not written by this project.

    PINNED against `unicodedata` 15.0.0 (Python 3.12).  A Python upgrade that
    ships a later Unicode will redden this DELIBERATELY wherever the classes
    gained a member: re-derive the ranges and re-review the additions.  Do not
    widen the oracle to make it pass -- that would restore exactly the
    self-validating shape this test exists to replace.
    """
    derived = {
        cp for cp in range(0x110000)
        if unicodedata.category(chr(cp)) in ("Cc", "Cf", "Zl", "Zp")
    } - darkside.PRESERVED_CODE_POINTS
    declared = {cp for lo, hi in darkside.COERCION_RANGES for cp in range(lo, hi + 1)}

    assert declared - derived == set(), (
        "declared but not a Cc/Cf/Zl/Zp code point: "
        f"{sorted(f'U+{c:04X}' for c in (declared - derived))}"
    )
    assert derived - declared == set(), (
        "in the classes the list claims to cover, but NOT declared: "
        f"{sorted(f'U+{c:04X}' for c in (derived - declared))}"
    )


def test_llr_coerce_1_tab_and_newline_are_preserved():
    """The two exceptions are DECLARED, so a silent third one cannot appear."""
    assert darkside.PRESERVED_CODE_POINTS == {0x09, 0x0A}
    for cp in darkside.PRESERVED_CODE_POINTS:
        assert darkside.plain(chr(cp)) == chr(cp)


def test_llr_coerce_1_the_carriage_return_is_coerced_not_preserved():
    """U+000D is IN the C0 range this list covers, and is easy to lose.

    An enumeration written as 0x00-0x08, 0x0B-0x0C, 0x0E-0x1F reads as "C0
    except TAB and LF" and silently also drops CR -- 29 points where C0 minus
    TAB and LF is 30.  Adopting it would have NARROWED the shipped coverage and
    let a carriage return reach the terminal, where it returns the cursor to
    column 0 and overprints the row already painted.
    """
    assert darkside.plain("a" + chr(0x0D) + "b") != "a" + chr(0x0D) + "b"
    covered = {cp for lo, hi in darkside.COERCION_RANGES for cp in range(lo, hi + 1)}
    assert {c for c in range(0x00, 0x20) if c not in (0x09, 0x0A)} <= covered


def test_llr_coerce_1_the_list_is_declared_exactly_once():
    """`M-COERCE.1-b`: widen the map with a literal list and declare the ranges
    beside it.  Both green on the day; they drift the first time one is edited.
    """
    sources = tracked_sources()
    declarations = [
        p for p, blob in sources.items()
        if re.search(r"^COERCION_RANGES\b", blob, re.M)
    ]
    assert declarations == ["mapper/darkside.py"]


def test_llr_coerce_1_no_test_retypes_the_range_list():
    """Every threshold and every test reads the list from the declaration.

    The input set is the DIRECTORY, deliberately not `git ls-files`.  Measured:
    with the git-tracked list, planting a second declaration in this very file
    reddened nothing, because a test file added by the increment under review is
    still UNTRACKED -- so the sweep was blind exactly where new work lands.  The
    product-source census upstream keeps `git ls-files` because `LLR-S06.3.1`
    names that command and scopes it to TRACKED product source; this sweep has
    no such mandate and cannot afford the hole.
    """
    candidates = sorted(
        p for p in (REPO / "tests").rglob("*.py") if "__pycache__" not in p.parts
    )
    tracked = subprocess.run(["git", "ls-files", "tests/**/*.py", "tests/*.py"],
                             cwd=REPO, capture_output=True, text=True, check=True)
    assert {REPO / p for p in tracked.stdout.split()} <= set(candidates), (
        "the sweep does not cover every tracked test file"
    )
    assert Path(__file__) in candidates, "the sweep cannot see the file it lives in"

    # Sweep for the NAME and for the VALUE: a copy under a different identifier
    # is the same drift, and the name check alone cannot see it.
    offenders = [
        p.name for p in candidates
        if re.search(r"^\s*COERCION_RANGES\s*=", p.read_text(encoding="utf-8"), re.M)
        or (p != Path(__file__)
            and re.search(r"0x0?61C|0xFFF9|0xE007F", p.read_text(encoding="utf-8")))
    ]
    assert offenders == []
