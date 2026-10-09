"""Scratch: run the n16_4 scenario body (copied logic, via the real test function) N times in one process.
Counts failures + records which keys were 'work but not painted'."""
import os, sys, collections
sys.path.insert(0, os.getcwd())
import pytest
from tests.test_help_scope import test_hlr_n16_4_legend_declares_its_own_keys as real, LAYOUT_SIZES

N = int(os.environ.get("SPIKE_N", "30"))
SIZES = [LAYOUT_SIZES[int(i)] for i in os.environ.get("SPIKE_SIZES", "0,1,2").split(",")]

async def test_repeat(tmp_path_factory, capsys):
    fails = collections.Counter(); runs = 0
    for i in range(N):
        for size in SIZES:
            runs += 1
            try:
                await real(tmp_path_factory.mktemp("r"), size)
            except AssertionError as e:
                fails[str(e).splitlines()[0][:120]] += 1
                with capsys.disabled(): print("FAIL", size, str(e)[:200], flush=True)
    with capsys.disabled():
        print(f"\nREPEAT runs={runs} fails={sum(fails.values())} {dict(fails)}")
