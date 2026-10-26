"""The read-only audit entry: ``audit(repo) -> Report`` (HLR-RH.7).

``mapper --audit <repo>`` runs headless: it discovers the connected repo
with ``git rev-parse --show-toplevel`` (the ``<repo>`` argument overrides),
loads and verifies the chain, derives the states, evaluates the release
rules and renders the report — chain status, the exact per-state counts
(pre-reviews and unentitled reviews counted separately, the informative
mark shown, the R17 old-head WARN lines), the identity ceiling sentence and
the verdict.  Exit semantics live in the CLI entry (``run_cli`` below, which
``app.main`` dispatches ``--audit`` to after the UTF-8 re-wrap): 0 on
``ready``, 1 otherwise.

Read-only means READ-ONLY (R4): the parse cache is OFF
(``ParseCache.disabled()`` — nothing is remembered, nothing saved) and
nothing anywhere is written — no ``git status`` either (R27a: the dirty
flag is ``Baseline.create``-only), so even git's own bookkeeping
(``.git/index``) is byte-identical after a run.  A ``safe.directory``
refusal or ANY git non-zero exit becomes the NAMED result ``no repo`` in
the report (R27d), never a crash.  Confinement (M1): the repo argument is
the operator's choice — it is resolved as given (relative paths and ``..``
allowed) and required to be an existing directory, with a LINK in the
argument itself refused by name before anything below it is read; the
toplevel then comes from ``git rev-parse --show-toplevel`` and every
registry file read under ``<toplevel>/reqharness/`` or
``REQUIREMENTS.md`` is swept (``baseline.confinement_sweep``) — a file or
link resolving outside the toplevel is refused by name, never followed.
"""
from __future__ import annotations

import os
import sys
import unicodedata
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from itertools import islice
from pathlib import Path

from mapper.osopen import is_link
from mapper.reqharness import baseline as _baseline
from mapper.reqharness import identity
from mapper.reqharness.cache import ParseCache
from mapper.reqharness.config import REQHARNESS_DIR, load_config
from mapper.reqharness.derive import (
    STATE_CHANGED,
    STATE_NOT_REVIEWED,
    STATE_PRE_REVIEWED,
    STATE_RETIRED,
    STATE_REVIEWED,
    Derivation,
    derive_states,
    load_canon,
)
from mapper.reqharness.records import ValidationError
from mapper.reqharness.release import (
    RULE_CHAIN,
    RULE_POLICY,
    RULE_SIGNERS,
    VERDICT_NOT_VERIFIABLE,
    Verdict,
    evaluate,
    safe_verify,
)
from mapper.reqharness.reviews import load_reviews

#: The report's per-state count order — every state prints, even at 0.
STATE_ORDER = (STATE_REVIEWED, STATE_CHANGED, STATE_PRE_REVIEWED, STATE_NOT_REVIEWED, STATE_RETIRED)

IDENTITY_CEILING = (
    "identity ceiling: git identity is self-claimed and spoofable by any "
    "committer; the chain proves integrity and approval, not authorship "
    "(LLR-RH.4.4)"
)

#: The named chain status for a repository that is a git repo but has no
#: registry at all — `reqharness/` absent (QA C1: the operator-facing
#: `--audit` names this state instead of the alarming `chain broken`).
NO_REGISTRY = "no registry yet"
VERDICT_NO_REGISTRY = "not ready · no registry yet"

#: The extra lines `run_cli` prints after the report when a hook is given (LLR-RMU.1.1).  The
#: verdict is found by its PREFIX `verdict: `: it is no longer the last line of the output.
HOOK_LINE_LIMIT = 1000
#: The per-line bound on a hook line AFTER the escape pass (LLR-RVU.1.1, ruling
#: `LED-2026-10-25-r2.02`): longer than 240 characters -> cut at 239 with one
#: trailing ellipsis, never splitting an escape spelling.  The bound predicates
#: over the EMITTED (escaped) form — a cut on the raw line would count escape
#: sequences as one cell each and mis-measure every hostile payload (C-42).
HOOK_LINE_CELLS = 240
STRUCTURE_NO_REPO = "structure: unavailable (no repository)"
STRUCTURE_NO_REGISTRY = "structure: unavailable (no registry)"
STRUCTURE_TRUNCATED = f"structure: output truncated at {HOOK_LINE_LIMIT} lines"


def _visible(value: object) -> str:
    """SEC F1 — every registry-derived value paints as VISIBLE text: C0 and
    C1 control characters, ESC, DEL and CR/LF render as their ``\\xNN``
    spellings, and every Unicode format/separator char (categories Cf, Zl,
    Zp — bidi overrides U+202A–U+202E / U+2066–U+2069, zero-width
    U+200B–U+200F / U+2060 / U+FEFF, line/paragraph separators U+2028 /
    U+2029), every space separator other than the plain U+0020 space
    (NBSP U+00A0, narrow NBSP U+202F, ideographic U+3000, the U+2000–U+200A
    range — an invisible or width-spoofing space in a crafted id), every
    combining mark (Mn nonspacing / Me enclosing — a combining sequence can
    overlay or reorder glyphs) and every variation selector (U+FE00–U+FE0F,
    U+E0100–U+E01EF — an emoji-presentation swap on a spoofed line) renders
    as its ``\\uXXXX`` spelling, so a crafted object id, reviewer id, hash or
    file name can never inject a terminal escape sequence, reverse the
    display or spoof a report line (e.g. a second, forged ``verdict:`` line
    — U+2028 splits ``str.splitlines()``)."""
    out: list[str] = []
    for ch in str(value):
        code = ord(ch)
        if code < 0x20 or code == 0x7F or 0x80 <= code <= 0x9F:
            out.append(f"\\x{code:02x}")
        elif (
            unicodedata.category(ch) in ("Cf", "Zl", "Zp", "Mn", "Me")
            or (unicodedata.category(ch) == "Zs" and code != 0x20)
            or 0xFE00 <= code <= 0xFE0F
            or 0xE0100 <= code <= 0xE01EF
        ):
            out.append(f"\\u{code:04x}")
        else:
            out.append(ch)
    return "".join(out)


def _cut_hook_line(shown: str) -> str:
    """The per-line bound on an ESCAPED hook line (LLR-RVU.1.1): longer than
    `HOOK_LINE_CELLS` (240) -> the first 239 cells plus one trailing ellipsis,
    so the emitted line is never longer than the bound itself.

    The cut never splits an escape spelling `_visible` produced: when the
    239-cell boundary lands inside a ``\\xNN`` / ``\\uXXXX`` spelling, the kept
    part backs to the spelling's start — a spelling is emitted whole or not at
    all, so the emitted tail can never end mid-spelling (AT-152 straddling
    arm).  The verdict-prefix rewrite is NOT this function's job: the pipeline
    order is pinned by F-SEC-3 as escape -> cut -> rewrite check -> print.
    """
    if len(shown) <= HOOK_LINE_CELLS:
        return shown
    kept = shown[: HOOK_LINE_CELLS - 1]
    slash = kept.rfind("\\")
    while slash != -1:
        if shown.startswith("\\x", slash):
            width = 4
        elif shown.startswith("\\u", slash):
            width = 6
        else:  # a lone backslash this sink never produces
            width = 1
        if slash + width <= len(kept):  # the spelling is whole in the cut
            break
        kept = kept[:slash]  # straddle: back to the spelling's start
        slash = kept.rfind("\\")  # adjacent spellings re-check their own tail
    return kept + "…"


@dataclass(frozen=True)
class Report:
    """The audit report: everything the CLI prints, as values."""

    repo: str
    chain_status: str
    verifiable: bool
    counts: dict[str, int]
    pre_reviewed: tuple[str, ...]
    unentitled: tuple[str, ...]
    informative_marks: tuple[str, ...]
    warnings: tuple[str, ...]
    reported: tuple[str, ...]
    verdict: str
    ready: bool
    rules: tuple[tuple[str, bool], ...] = ()
    baseline_name: str | None = None
    baseline_diff: _baseline.DiffResult | None = None


def _confine_repo(repo: str | Path) -> Path:
    """Resolve the operator's repo argument BEFORE any registry file is
    read (M1): the argument itself is the operator's choice — relative
    paths and ``..`` are allowed and resolved against the cwd — but a
    component of the GIVEN path that is a link is refused, by name, before
    anything below it is read.  The resolved argument must then be an
    existing directory; the toplevel and the registry-read confinement are
    established after it, through ``identity.repo_root`` and
    ``baseline.confinement_sweep``.  Every refusal is named, never a
    traceback."""
    text = str(repo)
    try:
        given = Path(text).expanduser()
        if not given.is_absolute():
            given = Path.cwd() / given
    except (OSError, ValueError, RuntimeError):
        raise ValidationError(f"{text}: refused (unreadable)") from None
    probe = Path(given.anchor)
    for part in given.parts[1:]:
        probe = probe / part
        try:
            info = os.lstat(probe)
        except (FileNotFoundError, NotADirectoryError):
            break  # the tail is missing: the is_dir check below names it
        except (OSError, ValueError):
            raise ValidationError(f"{text}: refused (unreadable)") from None
        if is_link(info):
            raise ValidationError(f"{text}: refused (link)") from None
    try:
        resolved = given.resolve()
    except (OSError, ValueError, RuntimeError):
        raise ValidationError(f"{text}: refused (unreadable)") from None
    if not resolved.is_dir():
        raise ValidationError(f"{text}: refused (not a directory)")
    return resolved


def _no_repo_report(root: Path) -> Report:
    """The named `no repo` result (R27d): a safe.directory refusal or any
    git non-zero exit lands here — on the audit report as on the screen."""
    zero = {state: 0 for state in STATE_ORDER}
    return Report(
        repo=str(root),
        chain_status=identity.NO_REPO,
        verifiable=False,
        counts=zero,
        pre_reviewed=(),
        unentitled=(),
        informative_marks=(),
        warnings=(),
        reported=(),
        verdict="not ready · no repo",
        ready=False,
    )


def _no_registry_report(root: Path) -> Report:
    """The named `no registry yet` result (QA C1): the repository is a
    usable git repo but has no `reqharness/` registry at all — a named
    state, not the alarming `chain broken` (nothing is broken; nothing was
    ever created)."""
    zero = {state: 0 for state in STATE_ORDER}
    return Report(
        repo=str(root),
        chain_status=NO_REGISTRY,
        verifiable=False,
        counts=zero,
        pre_reviewed=(),
        unentitled=(),
        informative_marks=(),
        warnings=(),
        reported=(),
        verdict=VERDICT_NO_REGISTRY,
        ready=False,
    )


def audit(repo: str | Path, *, baseline: str | None = None) -> Report:
    """The read-only audit (cache OFF, writes nothing).  Raises
    ValidationError only for the confinement refusals above — every other
    degradation is a named status inside the report."""
    root = _confine_repo(repo)
    top = identity.repo_root(root)
    if top == identity.NO_REPO:
        return _no_repo_report(root)
    root = Path(top)
    _baseline.confinement_sweep(root)
    if not (root / REQHARNESS_DIR).is_dir():
        return _no_registry_report(root)

    report = safe_verify(root)
    config = None
    if report.ok:
        # verify_chain already loaded and validated the config on this
        # path; a broken chain/policy never reaches the config rules.
        config = load_config(root)
    scan = load_reviews(root, cache=ParseCache.disabled())
    canon, canon_reported = (), ()
    canon_unreadable: str | None = None
    try:
        canon, canon_reported = load_canon(root)
    except ValidationError as exc:
        # M2: a missing / non-UTF-8 canon must not hide the chain status —
        # the report still prints the status and the (zero) per-state
        # counts it can compute, plus the named line, and stays not ready.
        canon_unreadable = str(exc)
    if config is None:
        derivation: Derivation = Derivation(
            verifiable=False, reason=report.status, reported=tuple(scan.reported)
        )
        verdict = Verdict(
            ready=False,
            text=VERDICT_NOT_VERIFIABLE,
            rules=((RULE_CHAIN, False), (RULE_POLICY, False), (RULE_SIGNERS, False)),
        )
    elif canon_unreadable is not None:
        derivation = Derivation(
            verifiable=False,
            reason="canon unreadable",
            reported=tuple(scan.reported),
        )
        verdict = Verdict(
            ready=False,
            text="not ready · canon unreadable",
            rules=((RULE_CHAIN, False), (RULE_POLICY, False), (RULE_SIGNERS, False)),
        )
    else:
        derivation = derive_states(canon, scan, report, config)
        verdict = evaluate(config, report, derivation)

    counts = {state: 0 for state in STATE_ORDER}
    for state in derivation.states.values():
        counts[state] = counts.get(state, 0) + 1

    diff_result = None
    if baseline is not None:
        frozen = _baseline.Baseline.load(root, baseline)
        data = _baseline.snapshot(root, scan=scan)
        diff_result = _baseline.diff(
            frozen, data.objects, current_review_files=data.review_files
        )

    return Report(
        repo=str(root),
        chain_status=report.status,
        verifiable=derivation.verifiable,
        counts=counts,
        pre_reviewed=derivation.pre_reviewed,
        unentitled=derivation.unentitled,
        informative_marks=derivation.informative_marks,
        warnings=derivation.warnings,
        reported=(
            tuple(derivation.reported)
            + tuple(canon_reported)
            + (
                (f"canon unreadable: {canon_unreadable}",)
                if canon_unreadable is not None
                else ()
            )
        ),
        verdict=verdict.text,
        ready=verdict.ready,
        rules=verdict.rules,
        baseline_name=baseline,
        baseline_diff=diff_result,
    )


def render(report: Report) -> str:
    """The exact report text the CLI prints: chain status, the per-state
    counts (pre-reviews and unentitled counted separately, the informative
    mark shown), the WARN lines, then the verdict.  SEC F1: every
    registry-derived value passes through `_visible` — a crafted object id,
    reviewer id or file name paints as visible ``\\xNN`` escapes and can
    never inject terminal control sequences or spoof a report line."""
    lines = [
        f"repo: {_visible(report.repo)}",
        f"chain: {_visible(report.chain_status)}",
        "counts: "
        + ", ".join(
            f"{_visible(state)}={report.counts.get(state, 0)}" for state in STATE_ORDER
        ),
        f"pre-reviews: {len(report.pre_reviewed)}"
        + (
            f" ({', '.join(_visible(item) for item in report.pre_reviewed)})"
            if report.pre_reviewed
            else ""
        ),
        f"unentitled reviews: {len(report.unentitled)}"
        + (
            f" ({', '.join(_visible(item) for item in report.unentitled)})"
            if report.unentitled
            else ""
        ),
    ]
    if report.informative_marks:
        lines.append(
            "informative marks: "
            + ", ".join(
                f"{_visible(object_id)} (changed (informative))"
                for object_id in report.informative_marks
            )
        )
    for warning in report.warnings:
        lines.append(f"WARNING: {_visible(warning)}")
    for line in report.reported:
        lines.append(f"reported: {_visible(line)}")
    if report.baseline_diff is not None:
        diff_result = report.baseline_diff
        lines.append(
            f"baseline {_visible(report.baseline_name)}: dirty="
            + ("true" if diff_result.baseline_dirty else "false")
        )
        for class_name in (
            _baseline.CLASS_NEW,
            _baseline.CLASS_CHANGED,
            _baseline.CLASS_UNCHANGED,
            _baseline.CLASS_RETIRED,
            _baseline.CLASS_DELETED,
        ):
            lines.append(
                f"{class_name}: "
                + ", ".join(_visible(name) for name in diff_result.by_class(class_name))
            )
        for name in diff_result.deleted_reviews:
            lines.append(f"deleted review: {_visible(name)}")
    lines.append(f"identity: {IDENTITY_CEILING}")
    lines.append(f"verdict: {_visible(report.verdict)}")
    return "\n".join(lines)


def _hook_lines(report: Report, extra_lines: Callable[[Path], Iterable[str]]) -> list[str]:
    """The lines printed after the report for a hook (LLR-RMU.1.1): one fixed line for the no-repo
    and no-registry reports (told apart by `chain_status`, never by verdict text, and the hook is
    NOT called), else at most `HOOK_LINE_LIMIT` lines of one call of the hook (a 1,001st is not
    consumed past, and one truncation line follows), or one `internal error` line when the hook
    raises.  The caller escapes, per-line bounds and ``verdict: ``-rewrites
    every line, in the F-SEC-3 order (escape -> cut -> rewrite check -> print)."""
    if report.chain_status == identity.NO_REPO:
        return [STRUCTURE_NO_REPO]
    if report.chain_status == NO_REGISTRY:
        return [STRUCTURE_NO_REGISTRY]
    try:
        lines = [str(line) for line in islice(extra_lines(Path(report.repo)), HOOK_LINE_LIMIT + 1)]
    except Exception as exc:  # the hook is informational: it never changes the exit code
        return [f"structure: unavailable (internal error: {type(exc).__name__})"]
    if len(lines) > HOOK_LINE_LIMIT:
        return lines[:HOOK_LINE_LIMIT] + [STRUCTURE_TRUNCATED]
    return lines


def run_cli(
    argv: list[str], extra_lines: Callable[[Path], Iterable[str]] | None = None
) -> int:
    """``mapper --audit <repo> [--baseline <name>]`` — the read-only audit
    entry (HLR-RH.7): prints the report and returns 0 on ``ready`` / 1
    otherwise, WITHOUT starting the TUI and without writing anything
    (R4 — the parse cache is OFF, no ``git status`` runs).  ``app.main``
    dispatches ``--audit`` here after the UTF-8 re-wrap and turns the
    returned code into the process exit status.

    ``extra_lines`` (HLR-RMU.1, injected by ``app`` so this module imports nothing from the
    relation-map package) is called once with the repository root and its lines are printed after
    the report through the report's own escaper; it never changes the exit code.  ``None`` is
    byte-identical to the behaviour before the hook existed.  When ``audit`` refuses (no report
    exists) the hook is not called and no structure line is printed."""
    index = argv.index("--audit")
    if index + 1 >= len(argv) or argv[index + 1].startswith("--"):
        print("usage: mapper --audit <repo> [--baseline <name>]", file=sys.stderr)
        return 2
    repo = argv[index + 1]
    baseline = None
    if "--baseline" in argv[index + 2 :]:
        bindex = argv.index("--baseline", index + 2)
        if bindex + 1 >= len(argv) or argv[bindex + 1].startswith("--"):
            print("usage: mapper --audit <repo> [--baseline <name>]", file=sys.stderr)
            return 2
        baseline = argv[bindex + 1]
    try:
        report = audit(Path(repo), baseline=baseline)
    except ValidationError as exc:
        # the named refusal — through the escaper like every other line, so
        # a control/bidi char in the operator's argument cannot inject
        # terminal control sequences even on the failure path (SEC F1 nit)
        print(f"audit: {_visible(exc)}", file=sys.stderr)
        return 1
    except Exception as exc:  # defence in depth (H1): never a traceback
        print(f"audit: internal error ({type(exc).__name__})", file=sys.stderr)
        return 1
    print(render(report))
    if extra_lines is not None:
        # F-SEC-3 pins the pipeline order verbatim: escape -> per-line cut ->
        # `verdict: ` rewrite check -> print.  The cut predicates over the
        # EMITTED (escaped) form and never splits an escape spelling
        # (LLR-RVU.1.1); the rewrite runs on the CUT line, so a hook line cut
        # short still cannot re-expose `verdict: ` to line start.
        for line in _hook_lines(report, extra_lines):
            shown = _cut_hook_line(_visible(line))
            if shown.startswith("verdict: "):  # `verdict: ` belongs to the report alone
                shown = "structure: " + shown
            print(shown)
    return 0 if report.ready else 1


__all__ = [
    "HOOK_LINE_LIMIT",
    "IDENTITY_CEILING",
    "NO_REGISTRY",
    "Report",
    "STATE_ORDER",
    "VERDICT_NO_REGISTRY",
    "audit",
    "render",
    "run_cli",
]
