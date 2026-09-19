"""Shared pytest fixtures for mapper tests."""
from __future__ import annotations

import os
import subprocess

import pytest

from mapper.store import MapStore

#: `pytester` runs a nested pytest session.  It is here for exactly one arm:
#: the lane guard's teardown half only bites when product code SWALLOWS the
#: refusal, and an arm cannot observe its own teardown failing from inside
#: itself.  See tests/test_hermetic.py.
pytest_plugins = ["pytester"]


@pytest.fixture
def tmp_store(tmp_path):
    """A MapStore backed by a temporary workspace."""
    ws = tmp_path / "workspace"
    return MapStore(ws)


# --------------------------------------------------------------------------
# HERMETIC-1: the default lane may not reach the network.
#
# The axis is not "this one arm shelled out to `gh`".  It is that the suite had
# an UNDECLARED EXTERNAL DEPENDENCY: it could not run offline, could not run
# without credentials, and its result depended on a third party's availability.
# Mocking the one arm that was caught fixes the instance; this guard holds the
# axis, so the next arm that reaches out reddens instead of being discovered by
# a timeout months later.
#
# The classification is deliberately per-INVOCATION, not per-executable.  `git`
# is the product's local reader (`git show`, `git log`, `git rev-list`) AND its
# remote fetcher (`git clone`, `git fetch`); a per-executable rule would have to
# ban the local reads too, and the whole of `tests/test_github.py` drives real
# local repositories on purpose.  A ban that broad gets routed around.
# --------------------------------------------------------------------------

#: Executables whose every invocation reaches a remote.
#:
#: `gh` is the one this product actually spawns.  The rest are here because the
#: population this guard protects is THE NEXT TEST AUTHOR rather than today's
#: tree: a lane that refuses `gh` and waves `curl` through is sampling the axis,
#: not holding it.  Each name costs nothing and removes one way to reach the
#: network by accident.
_ALWAYS_REMOTE = frozenset(
    {"gh", "curl", "wget", "ssh", "scp", "rsync", "pip", "pip3", "npm", "npx", "yarn"}
)

#: `git` subcommands that contact a remote.  Everything else `git` offers is a
#: local read of the object store and stays legal in the default lane.
#:
#: `remote` and `submodule` WERE here and are not: `git remote -v`,
#: `git remote get-url` and `git submodule status` contact nothing, and this
#: module's whole argument for classifying per-INVOCATION is that local git
#: stays legal.  A table that bans local readers is the over-broad ban it exists
#: to avoid, and an over-broad guard is precisely what gets routed around.
#:
#: The update-style forms (`git remote update`, `git submodule update`) DO reach
#: a remote and are left legal rather than special-cased on a second token:
#: nothing in this product or this suite issues them, so a branch for them would
#: be a rule with no subject and no arm -- untested by construction.  Declared
#: here rather than silently omitted.
_REMOTE_GIT_SUBCOMMANDS = frozenset({"clone", "fetch", "pull", "push", "ls-remote"})


class HermeticViolation(RuntimeError):
    """Raised when a test in the default lane tries to reach the network."""


def _executable(argv) -> str:
    """The bare executable name from a subprocess argv, or '' if not derivable."""
    try:
        head = argv[0]
    except (TypeError, IndexError, KeyError):
        return ""
    if not isinstance(head, str):
        head = str(head)
    return head.rsplit("/", 1)[-1].rsplit("\\", 1)[-1].removesuffix(".exe").lower()


def network_reaching(argv) -> tuple[bool, str]:
    """Classify a subprocess argv.  Returns (reaches_network, reason).

    Pure, so it can be asserted directly without installing the guard -- and the
    guard consults THIS function, so an arm over it is an arm over the guard's
    real decision rather than over a restatement of it.
    """
    # A STRING COMMAND IS REFUSED RATHER THAN PARSED.  `shell=True` takes a
    # command LINE, and tokenising one correctly enough to classify it means
    # reimplementing a shell -- quoting, `&&`, substitution, `$PATH` lookup.
    # This guard would be guessing, and a guard that guesses wrong in the
    # permissive direction is worse than no guard, because the lane's green now
    # ASSERTS hermeticity.  Nothing in this product or suite spawns a string, so
    # refusing costs nothing today and fails closed if that changes.
    if isinstance(argv, (str, bytes)):
        return True, (
            "a string command cannot be classified without reimplementing a shell, "
            "so it is refused rather than guessed at; pass an argv list"
        )
    exe = _executable(argv)
    if not exe:
        return False, ""
    if exe in _ALWAYS_REMOTE:
        return True, f"`{exe}` is a remote API client; every invocation reaches the network"
    if exe == "git":
        # Find the SUBCOMMAND, which is the first token that is neither a
        # pre-subcommand option nor that option's value.  `-C` and `-c` each
        # take a value, and skipping the flag but not its value reads a
        # directory path as the subcommand -- which silently lets the product's
        # real `git -C <path> fetch --all` through.
        rest = [str(t) for t in list(argv)[1:]]
        i = 0
        while i < len(rest):
            token = rest[i]
            if token in ("-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"):
                i += 2
                continue
            if token.startswith("-"):
                i += 1
                continue
            if token in _REMOTE_GIT_SUBCOMMANDS:
                return True, f"`git {token}` contacts a remote"
            break
    return False, ""


@pytest.fixture(autouse=True)
def _hermetic_lane(request, monkeypatch):
    """Refuse network-reaching subprocesses outside the `network` lane.

    Two halves, and the second is the load-bearing one:

    * the call is REFUSED, so the default lane cannot depend on a third party;
    * the refusal is also RECORDED and asserted at teardown, because product
      code swallows exceptions.  `RepoScreen.on_mount` catches bare `Exception`
      and notifies -- so a guard that only raised would be absorbed and the arm
      would stay green while the defect was still there.  A guard whose verdict
      can be swallowed is not a guard.
    """
    violations: list[str] = []
    if request.node.get_closest_marker("network") is not None:
        yield violations
        return

    real_run = subprocess.run
    real_popen = subprocess.Popen
    real_system = os.system

    def _check(argv):
        reaches, reason = network_reaching(argv)
        if reaches:
            shown = argv if isinstance(argv, str) else " ".join(str(a) for a in argv)
            shown = str(shown)[:120]
            violations.append(f"{shown}  --  {reason}")
            raise HermeticViolation(
                f"the default lane may not reach the network: {shown}\n"
                f"reason: {reason}\n"
                "mock the seam, or mark the test `network` and declare the dependency."
            )

    # `*args, **kwargs` rather than a named first parameter: `subprocess.run`
    # accepts its argv as the keyword `args=[...]`, and a wrapper that only took
    # it positionally raised `TypeError` naming an internal closure on a legal
    # offline call.  Fail-loud, so nothing reached the network -- but a guard
    # that false-fails correct work is as expensive as one that passes wrong
    # work, and this one would have been blamed on the caller.
    def _argv_of(args, kwargs):
        if args:
            return args[0]
        return kwargs.get("args", ())

    def guarded_run(*args, **kwargs):
        _check(_argv_of(args, kwargs))
        return real_run(*args, **kwargs)

    def guarded_popen(*args, **kwargs):
        _check(_argv_of(args, kwargs))
        return real_popen(*args, **kwargs)

    monkeypatch.setattr(subprocess, "run", guarded_run)
    monkeypatch.setattr(subprocess, "Popen", guarded_popen)
    # `os.system` takes a command STRING and bypasses `subprocess` entirely, so
    # neither patch above can see it.  Refused outright rather than classified:
    # see `network_reaching` on why a string command is not parseable here.
    monkeypatch.setattr(
        os,
        "system",
        lambda command: _check(command) or real_system(command),
    )
    yield violations
    assert not violations, (
        "HERMETIC-1: this test reached the network.\n  " + "\n  ".join(violations)
    )
