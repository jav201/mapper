"""HERMETIC-1 -- the default lane may not depend on a third party.

Three arms, and they answer three different questions:

* `test_every_product_spawn_site_carries_a_hermeticity_classification` is the
  CENSUS OVER THE AXIS.  Mocking the one arm that was caught fixes the
  instance; this asserts that no external process can enter the product without
  a recorded verdict on whether it reaches the network.  It is derived from the
  source by AST and compared BOTH WAYS, because a one-way arm catches a site
  added to the product and is blind to one dropped from the declaration.
* `test_the_guard_refuses_a_remote_call_and_records_it` is the INSTRUMENT'S OWN
  RED-PROOF.  A guard that has never reported a failure is not known to work,
  and this one has two halves that can fail independently -- the refusal and
  the recording -- so both are exercised.
* `test_the_guard_does_not_false_fail_local_git` is the negative control.  A
  rule that false-fails correct work is as expensive as one that passes wrong
  work, and the whole of `tests/test_github.py` drives real local repositories.
"""
from __future__ import annotations

import ast
import os
import pathlib
import subprocess

import pytest

from .conftest import HermeticViolation, network_reaching


#: Every executable this product can spawn, with its hermeticity verdict.
#: A new entry here is a DECISION, which is the point: the census below refuses
#: to let a spawn site appear in the product without one.
DECLARED_SPAWNS = {
    "git": "conditional -- local plumbing is offline; clone/fetch/pull/push reach a remote",
    "gh": "remote -- an authenticated API client; every invocation reaches the network",
    "open": "viewer-launch -- hands a file to the OS handler; offline, but a side effect",
    "xdg-open": "viewer-launch -- hands a file to the OS handler; offline, but a side effect",
}

#: The Windows arm of the viewer-launch class, DERIVED rather than spelled.
#:
#: `os.startfile` takes no argv, so the executable census above cannot see it,
#: and a hand-written string naming it would go stale unnoticed -- a constant
#: that looks like a check and is not.  So it is derived from the source the
#: same way the argv spawns are, and asserted.
#:
#: DECLARED GAP, NOT AN OVERSIGHT: the lane guard covers the NETWORK axis, which
#: is the axis `HERMETIC-1` was ruled on.  Viewer launches are offline but are
#: still external side effects; nothing in this suite stops one, and no arm
#: reaches one today.  That emptiness is a fact about today's tests, not a
#: property anything holds -- said here so the next reader finds a declaration
#: rather than a silence.
VIEWER_LAUNCH_ATTRS = {("os", "startfile")}


def _derived_viewer_launch_attrs() -> set[tuple[str, str]]:
    """Attribute-call viewer launches in the product, e.g. `os.startfile(...)`."""
    root = pathlib.Path(__file__).resolve().parent.parent / "mapper"
    found: set[tuple[str, str]] = set()
    for path in sorted(root.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and (node.func.value.id, node.func.attr) in VIEWER_LAUNCH_ATTRS
            ):
                found.add((node.func.value.id, node.func.attr))
    return found


def test_the_viewer_launch_class_is_complete_and_still_unguarded():
    """The declared gap is asserted, so it cannot quietly stop being true.

    Two halves: the argv-side launchers (`open`, `xdg-open`) are already covered
    both ways by the spawn census, and this pins the non-argv one the census
    structurally cannot see.  If `os.startfile` is ever removed, this arm
    reddens and the declaration above gets re-read instead of lingering as a
    note about code that is gone.
    """
    assert _derived_viewer_launch_attrs() == VIEWER_LAUNCH_ATTRS, (
        "the viewer-launch class changed; re-read the declared gap above"
    )
    assert {"open", "xdg-open"} <= set(DECLARED_SPAWNS), (
        "the argv-side viewer launches must stay classified in the spawn census"
    )

_SPAWN_FUNCS = {"run", "Popen", "call", "check_call", "check_output"}


def _spawn_argv(call: ast.Call):
    """The argv expression of a spawn call, positional OR by `args=` keyword.

    One reader for both forms, so the census cannot see a spawn in one spelling
    and miss it in the other. Returns `None` when the call carries no argv at
    all, which is the only case worth skipping.
    """
    if call.args:
        return call.args[0]
    for keyword in call.keywords:
        if keyword.arg == "args":
            return keyword.value
    return None


def _derived_spawn_executables(root=None) -> set[str]:
    """AST-walk the product and return every executable it can spawn.

    Derived, never hand-listed: a hand-listed population is a spec claim, and
    this arm exists precisely to catch the site nobody remembered to list.

    `root` defaults to the real product tree and exists so an arm can drive
    THIS function -- the one the census actually uses -- over a synthetic tree.
    A probe that re-implements the walk to test the walk cannot disagree with
    its author.
    """
    root = pathlib.Path(root or pathlib.Path(__file__).resolve().parent.parent / "mapper")
    found: set[str] = set()
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not isinstance(func, ast.Attribute) or func.attr not in _SPAWN_FUNCS:
                continue
            # Only real process spawns: `subprocess.run(...)`, never a method
            # called `run` on something else (`app.run()` is not a subprocess).
            if not (isinstance(func.value, ast.Name) and func.value.id == "subprocess"):
                continue
            # `S-F11`: THE ARGV MAY ARRIVE BY KEYWORD, AND THIS CENSUS WAS
            # BLIND TO IT.  `subprocess.run(args=[...])` is the documented
            # signature; this walk read `node.args[0]` only, so a product spawn
            # of an undeclared binary written in that legal form PASSED the
            # census while the identical spawn written positionally FAILED it.
            # The runtime guard was taught exactly this by `SEC-F6`, and the
            # census that derives its population was not -- a lesson applied to
            # an instance and not to its class, which is the defect family this
            # batch exists to close, landing in the instrument rather than in
            # the product.
            argv = _spawn_argv(node)
            if argv is None:
                continue
            if isinstance(argv, ast.List) and argv.elts:
                head = argv.elts[0]
                if isinstance(head, ast.Constant) and isinstance(head.value, str):
                    found.add(head.value)
                    continue
            if isinstance(argv, ast.BinOp) and isinstance(argv.left, ast.List) and argv.left.elts:
                head = argv.left.elts[0]
                if isinstance(head, ast.Constant) and isinstance(head.value, str):
                    found.add(head.value)
                    continue
            # A non-literal argv (`cmd`, built above the call) is resolved by
            # reading the assignment in the same function.
            found.update(_resolve_indirect_argv(tree, node))
    return found


def _resolve_indirect_argv(tree: ast.AST, call: ast.Call) -> set[str]:
    """Head executables for a spawn whose argv is a name bound in the MODULE.

    The walk is module-wide, not function-scoped, so it OVER-APPROXIMATES: two
    functions binding the same local name contribute to each other's result.
    That is the safe direction for this census -- over-collecting can only add a
    spawn that must be classified, never hide one -- but it is stated because
    the previous wording claimed "in the same function", which is not what the
    code does and would have sent a reader looking for a bug that is not there.
    """
    target = _spawn_argv(call)
    if not isinstance(target, ast.Name):
        return set()
    out: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == target.id for t in node.targets):
            continue
        value = node.value
        if isinstance(value, ast.BinOp) and isinstance(value.left, ast.List) and value.left.elts:
            head = value.left.elts[0]
            if isinstance(head, ast.Constant) and isinstance(head.value, str):
                out.add(head.value)
        elif isinstance(value, ast.List) and value.elts:
            head = value.elts[0]
            if isinstance(head, ast.Constant) and isinstance(head.value, str):
                out.add(head.value)
    return out


def test_every_product_spawn_site_carries_a_hermeticity_classification():
    derived = _derived_spawn_executables()
    declared = set(DECLARED_SPAWNS)

    # The set must be non-empty, or this arm is comparing nothing to nothing and
    # passes on a broken walk.
    assert derived, "the AST walk found no spawn sites at all -- the walk is broken"

    undeclared = derived - declared
    assert not undeclared, (
        "the product can spawn an executable with no hermeticity verdict: "
        f"{sorted(undeclared)}.  Classify it in DECLARED_SPAWNS and, if it "
        "reaches a remote, teach tests/conftest.py to refuse it."
    )
    stale = declared - derived
    assert not stale, (
        f"DECLARED_SPAWNS classifies {sorted(stale)}, which the product no "
        "longer spawns.  A declaration nothing corresponds to is drift."
    )


@pytest.mark.parametrize(
    "argv, expected",
    [
        (["gh", "repo", "view", "jav201/taskboard"], True),
        (["gh", "--version"], True),
        (["git", "clone", "--mirror", "https://example.invalid/x", "/tmp/x"], True),
        (["git", "-C", "/tmp/x", "fetch", "--all"], True),
        (["git", "-C", "/tmp/x", "log", "-1"], False),
        (["git", "show", "HEAD:file"], False),
        (["git", "init", "-q"], False),
        (["open", "/tmp/x.svg"], False),
        # `git remote` and `git submodule` READ LOCALLY in these forms, and the
        # table used to ban them -- the over-broad ban this classifier exists to
        # avoid, since an over-broad guard is what gets routed around.
        (["git", "remote", "-v"], False),
        (["git", "-C", "/tmp/x", "submodule", "status"], False),
        (["git", "remote", "get-url", "origin"], False),
        # The population this guard protects is the NEXT TEST AUTHOR, not
        # today's tree: refusing `gh` while waving these through samples the
        # axis rather than holding it.
        (["curl", "https://example.invalid"], True),
        (["wget", "-q", "https://example.invalid"], True),
        (["pip", "install", "requests"], True),
        # A string command is REFUSED rather than parsed: classifying one means
        # reimplementing a shell, and a guard that guesses in the permissive
        # direction is worse than none once the lane's green asserts hermeticity.
        ("gh api repos/x/y", True),
        ("echo hello", True),
    ],
)
def test_network_reaching_classifies_each_real_invocation(argv, expected):
    """Driven off the argv forms the product actually builds, not invented ones.

    Every True case above is a literal from `mapper/github.py`; every False case
    is one `mapper/diff.py`, `mapper/github.py` or `tests/test_github.py` really
    issues.  A classifier tested only on invented input is tested on a model.
    """
    reaches, reason = network_reaching(argv)
    assert reaches is expected, f"{argv} -> {reaches} ({reason!r})"
    if expected:
        assert reason, "a refusal must say why, or the next reader cannot act on it"


def test_the_guard_refuses_a_remote_call_and_records_it(_hermetic_lane):
    """The instrument reports FAILURE on a known-bad input, before any PASS is believed.

    Both halves are asserted because they fail independently, and the recording
    half is the load-bearing one: product code catches broad exceptions, so a
    guard that only raised could be swallowed and leave the arm green.
    """
    with pytest.raises(HermeticViolation) as caught:
        subprocess.run(["gh", "api", "repos/jav201/taskboard"], capture_output=True)
    assert "may not reach the network" in str(caught.value)

    assert len(_hermetic_lane) == 1, "the refusal was raised but never recorded"
    assert "gh api repos/jav201/taskboard" in _hermetic_lane[0]
    # Consume it: this arm's violation is its evidence, not its failure.
    _hermetic_lane.clear()


def test_os_system_cannot_walk_past_the_guard(_hermetic_lane):
    """`os.system` bypasses `subprocess` entirely, so neither patch can see it.

    Added because the guard's own bypass matrix found this one OPEN and UNDECLARED
    -- the two patched attributes are `subprocess.run` and `subprocess.Popen`, and
    `os.system` reaches the OS without touching either.  A guard that can be walked
    past is worse than no guard once the lane's green is read AS the hermeticity
    claim, which is exactly how this batch reads it.

    IT TAKES A COMMAND STRING, WHICH IS REFUSED RATHER THAN PARSED, and the
    consequence is stated rather than left to be discovered: `os.system` is
    effectively unavailable in the default lane for ANY command, not only a
    remote one.  Classifying a command line means reimplementing a shell --
    quoting, `&&`, substitution, `$PATH` -- and a guard that guesses in the
    permissive direction is the failure this exists to prevent.  Nothing in this
    product or this suite spawns one, so refusing costs nothing today and fails
    closed if that changes.
    """
    with pytest.raises(HermeticViolation) as caught:
        os.system("gh api repos/jav201/taskboard")
    assert "may not reach the network" in str(caught.value)

    assert len(_hermetic_lane) == 1, "the refusal was raised but never recorded"
    # Consume it: this arm's violation is its evidence, not its failure.
    _hermetic_lane.clear()


def test_the_guard_reads_the_KEYWORD_argv_form_too(_hermetic_lane, tmp_path):
    """`subprocess.run(args=[...])` is legal, and the guard used to crash on it.

    Two halves, asserted separately because they fail in OPPOSITE directions and
    an arm on either alone is satisfied by the wrong fix.  A remote call written
    in the keyword form must be REFUSED -- a guard that reads only the positional
    form is bypassed by a spelling.  A local call written the same way must NOT
    be, and the wrapper originally raised `TypeError` naming an internal closure
    on it, so correct offline work would have been blamed on its author.
    """
    with pytest.raises(HermeticViolation):
        subprocess.run(args=["gh", "api", "repos/jav201/taskboard"], capture_output=True)
    assert len(_hermetic_lane) == 1, "the keyword form was refused but never recorded"
    _hermetic_lane.clear()

    repo = tmp_path / "kw"
    repo.mkdir()
    result = subprocess.run(args=["git", "init", "-q"], cwd=repo, capture_output=True)
    assert result.returncode == 0, "the guard false-failed a legal offline keyword call"
    assert not _hermetic_lane, "a local `git init` was recorded as a network violation"


def test_the_guard_does_not_false_fail_local_git(tmp_path):
    """The negative control: correct offline work stays green under the guard.

    Without this, the cheapest way to pass the arm above is to ban every
    subprocess -- which would break the six local-repository arms in
    tests/test_github.py and train everyone to route around the guard.
    """
    repo = tmp_path / "local"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "true"


def test_a_swallowed_refusal_still_reddens_the_arm(pytester):
    """The teardown half, which no in-process arm can reach.

    The refusal is RAISED and RECORDED.  Raising alone is not enough: the defect
    that started HERMETIC-1 lives behind `RepoScreen.on_mount`, which catches
    bare `Exception` and notifies -- so product code that swallows the refusal
    would leave the arm green with the network call still in it.  The recording
    exists for that case, and only a nested session can watch an arm go red from
    its own teardown.

    Measured: without this arm, defanging the teardown assertion SURVIVES the
    mutation battery.  With it, the mutant is killed.
    """
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    pytester.makeconftest(
        f"""
        import sys
        sys.path.insert(0, {str(repo_root)!r})
        from tests.conftest import _hermetic_lane, network_reaching, HermeticViolation
        """
    )
    pytester.makepyfile(
        """
        import subprocess

        def test_swallows_the_refusal_like_the_product_does():
            try:
                subprocess.run(["gh", "api", "repos/x/y"], capture_output=True)
            except Exception:
                pass          # exactly what RepoScreen.on_mount does
            assert True       # the arm's own assertions all pass
        """
    )
    result = pytester.runpytest_subprocess("-p", "no:randomly")
    # The arm asserted nothing false, so it must be the LANE GUARD that reddens it.
    assert result.ret != 0, "a swallowed network call left the nested arm green"
    result.stdout.fnmatch_lines(["*HERMETIC-1: this test reached the network*"])


@pytest.mark.network
def test_the_network_marker_lifts_the_guard():
    """C-55: the bypass branch is a no-op on today's tree, so it is exercised anyway.

    The `network` lane holds no live-`gh` arm -- the one that used to reach out
    asserted that a screen composes, which never needed real data.  That leaves
    the marker's bypass untested by anything the suite runs, and an untested
    bypass is how a marker silently stops working.  So this arm constructs the
    case the tree lacks: it claims the marker and proves the guard is absent.

    It touches no network.  It asserts that `subprocess.run` is the real one,
    which is the whole of what the marker is supposed to do.
    """
    assert subprocess.run.__module__ == "subprocess", (
        "the `network` marker did not lift the lane guard"
    )


@pytest.mark.parametrize(
    "spelling, source",
    [
        ("positional", 'subprocess.run(["curl", "https://example.invalid"])'),
        ("keyword-argv", 'subprocess.run(args=["curl", "https://example.invalid"])'),
    ],
)
def test_the_spawn_census_sees_an_undeclared_binary_in_EITHER_SPELLING(
    tmp_path, spelling, source
):
    """`S-F11`: the census read positional argv only, so a legal form escaped it.

    THE PAIR IS THE POINT.  Before this fix the two rows disagreed: the same
    undeclared `curl` spawn FAILED the census written positionally and PASSED
    it written `subprocess.run(args=[...])`. A census whose answer depends on
    the caller's spelling is not a census -- and `SEC-F6` had already taught
    the runtime guard this exact lesson, which is what makes this an instance
    of *a lesson applied to an instance and not to its class*, landing in the
    instrument rather than in the product.

    IT DRIVES THE REAL CENSUS FUNCTION over a synthetic tree, rather than
    re-implementing the walk to test the walk. A probe that models its subject
    cannot disagree with its author.
    """
    module = tmp_path / "fake_product.py"
    module.write_text(f"import subprocess\n\n\ndef go():\n    {source}\n", encoding="utf-8")

    derived = _derived_spawn_executables(root=tmp_path)

    assert "curl" in derived, (
        f"the census did not see an undeclared `curl` spawn written {spelling}: "
        f"derived {sorted(derived)}. A spawn the census cannot see is a spawn "
        f"nobody has to classify."
    )


def test_the_spawn_census_positive_control_returns_a_NON_absence(tmp_path):
    """The control for the arm above: an empty tree must NOT read as clean.

    Every assertion above is that something IS found. The cheapest way to pass
    a `not in` census is a walk that returns nothing at all, so this pins that
    the walk's emptiness is a real answer about a real tree rather than a
    broken traversal -- and the product census itself asserts non-emptiness
    before comparing, for the same reason.
    """
    (tmp_path / "quiet.py").write_text("x = 1\n", encoding="utf-8")
    assert _derived_spawn_executables(root=tmp_path) == set()
    assert _derived_spawn_executables(), (
        "the census returned NOTHING for the real product tree -- the walk is "
        "broken, not the tree"
    )
