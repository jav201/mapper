"""The ``--audit`` hook per-line bound 240 (LLR-RVU.1.1 — batch
`2026-10-25-relmap-r2-batch`, increment 7; AT-152, TC-RM-30).

The pipeline order pinned verbatim by F-SEC-3
(`PDR-2026-10-25-relmap-r2-batch#D4`):
escape -> 239+ellipsis spelling-aware cut -> ``verdict: `` rewrite check ->
print.  The bound predicates over the EMITTED (escaped) form (C-42).  The R1
D4 semantics — the 1,000-line count bound, the prefix rewrite, the fixed
no-repo/no-registry lines, the exit code — stay pinned by the unchanged R1
suite (`tests/test_relmap_audit.py`, TC-RM-02/03), run in this increment's
guard set.
"""
from __future__ import annotations

from mapper.reqharness import audit as audit_mod
from tests._relmap_fixtures import ONE_ROW, registry_repo

ELLIPSIS = "…"


def _run_hook(argv, hook, capsys):
    code = audit_mod.run_cli(argv, extra_lines=hook)
    out = capsys.readouterr()
    return code, out.out, out.err


# --------------------------------------------------------------------------- the sink


def test_llr_rvu_1_1_unit_boundaries_and_cut_shape(capsys):
    """TC-RM-30 unit arm on the cut itself: exactly 240 is untouched, 241 and
    beyond cut at 239 with one trailing ellipsis (240 emitted cells)."""
    cut = audit_mod._cut_hook_line
    assert cut("a" * 240) == "a" * 240, "the bound is STRICTLY longer-than-240"
    assert cut("b" * 241) == "b" * 239 + ELLIPSIS
    assert cut("c" * 500) == "c" * 239 + ELLIPSIS
    assert len(cut("d" * 1000)) == 240


def test_llr_rvu_1_1_unit_cut_never_splits_an_escape_spelling():
    """A ``\\xNN`` / ``\\uXXXX`` spelling straddling the 239-cell boundary
    backs the cut to the spelling's start — the spelling is emitted whole or
    not at all (AT-152 straddling arm, M-RVU-3)."""
    cut = audit_mod._cut_hook_line
    # 237 cells + one \xNN spelling (4 cells): the boundary lands at cell 239,
    # inside the spelling -> back to 237, ellipsis is the 238th cell.
    assert cut("x" * 237 + "\\x01") == "x" * 237 + ELLIPSIS
    # 235 cells + one \uXXXX spelling (6 cells): same back-off.
    assert cut("y" * 235 + "\\u202e") == "y" * 235 + ELLIPSIS
    # ADJACENT spellings: the back-off re-checks its own new tail.
    assert cut("z" * 236 + "\\x01" + "\\x02") == "z" * 236 + ELLIPSIS
    # A spelling ending EXACTLY at the boundary is kept whole.
    assert cut("w" * 235 + "\\x01") == "w" * 235 + "\\x01"
    # The cut itself never rewrites a verdict prefix (that check is the
    # pipeline's NEXT stage, pinned after the cut by F-SEC-3).
    assert cut("verdict: " + "v" * 400).startswith("verdict: ")


# --------------------------------------------------------------------------- AT-152 arms


def test_at_152_hook_line_longer_than_240_is_cut_with_one_ellipsis(tmp_path, capsys):
    """AT-152's driver limb: a hook line of 240 + N characters emits cut at
    239 with one ellipsis; the emitted line is at most 240 cells; a line of
    exactly 240 is untouched; the hook stays informational (exit code is the
    report's own)."""
    repo = registry_repo(tmp_path, "r", ONE_ROW)
    base_code, base_out, _ = _run_hook(["--audit", str(repo)], None, capsys)
    lines = ["a" * 240, "b" * 241, "c" * 300]
    code, out, _ = _run_hook(["--audit", str(repo)], lambda r: lines, capsys)
    emitted = out[len(base_out):].splitlines()
    assert code == base_code, "the hook never changes the exit code (R1 D4)"
    assert emitted == ["a" * 240, "b" * 239 + ELLIPSIS, "c" * 239 + ELLIPSIS]
    assert all(len(line) <= 240 for line in emitted)


def test_at_152_the_bound_predicates_over_the_escaped_form(tmp_path, capsys):
    """M-RVU-1: the bound counts the EMITTED (escaped) form, never the raw
    line — 60 raw control chars (62 cells) escape to 242 cells and MUST cut;
    a cut on the raw line would leave all 60 spellings and emit 242 cells."""
    repo = registry_repo(tmp_path, "r", ONE_ROW)
    base_code, base_out, _ = _run_hook(["--audit", str(repo)], None, capsys)
    payload = "ab" + "\x01" * 60
    code, out, _ = _run_hook(["--audit", str(repo)], lambda r: [payload], capsys)
    emitted = out[len(base_out):].splitlines()
    assert code == base_code
    # "ab" + 59 whole spellings + the ellipsis; the 60th spelling (straddling
    # cell 239) is dropped whole, never split.
    assert emitted == ["ab" + "\\x01" * 59 + ELLIPSIS], emitted
    assert len(emitted[0]) == 239
    assert "\x01" not in out, "a raw control char reached the terminal"


def test_at_152_a_straddling_escape_spelling_backs_to_its_start(tmp_path, capsys):
    """AT-152 straddling arm (SEC-1 / M-RVU-3): an escape spelling straddling
    byte 240 is cut at a spelling boundary — the emitted line never ends
    mid-spelling — for both the ``\\xNN`` and the ``\\uXXXX`` classes."""
    repo = registry_repo(tmp_path, "r", ONE_ROW)
    base_code, base_out, _ = _run_hook(["--audit", str(repo)], None, capsys)
    payloads = ["x" * 237 + "\x01", "y" * 235 + "\u202e"]
    code, out, _ = _run_hook(["--audit", str(repo)], lambda r: payloads, capsys)
    emitted = out[len(base_out):].splitlines()
    assert code == base_code
    assert emitted == ["x" * 237 + ELLIPSIS, "y" * 235 + ELLIPSIS], emitted
    for line in emitted:
        kept = line[:-1]  # the ellipsis occupies the last cell
        assert not kept.endswith("\\"), f"mid-spelling cut: {kept[-8:]!r}"
        assert len(line) <= 240


def test_at_152_verdict_prefixed_hook_line_is_cut_then_rewritten(tmp_path, capsys):
    """F-SEC-3's pinned order observable end to end: escape -> cut -> rewrite
    check -> print.  A ``verdict: ``-starting hook line longer than 240 emits
    ``structure: `` + the 240-cell CUT form (250 cells total): the rewrite
    runs on the CUT line, never re-exposing ``verdict: `` to line start, and
    never before the cut (M-RVU-2)."""
    repo = registry_repo(tmp_path, "r", ONE_ROW)
    _base_code, base_out, _ = _run_hook(["--audit", str(repo)], None, capsys)
    code, out, _ = _run_hook(
        ["--audit", str(repo)], lambda r: ["verdict: " + "v" * 300], capsys)
    hook_line = out[len(base_out):].splitlines()[-1]
    # cut first: "verdict: " + 230 cells + ellipsis (240); then the rewrite.
    assert hook_line == "structure: " + "verdict: " + "v" * 230 + ELLIPSIS, hook_line
    assert len([ln for ln in out.splitlines() if ln.startswith("verdict: ")]) == 1, (
        "`verdict: ` stays exclusive to the report's own line (R1 D4)"
    )


def test_at_152_hook_line_under_the_bound_passes_through_untouched(tmp_path, capsys):
    """A hook line whose ESCAPED form is under the bound is emitted byte for
    byte — escapes and all."""
    repo = registry_repo(tmp_path, "r", ONE_ROW)
    _base_code, base_out, _ = _run_hook(["--audit", str(repo)], None, capsys)
    payload = "ok: " + "\x02" * 58  # escapes to 4 + 232 = 236 cells
    _code, out, _ = _run_hook(["--audit", str(repo)], lambda r: [payload], capsys)
    assert out[len(base_out):].splitlines() == ["ok: " + "\\x02" * 58]
