"""Inc-3 mutation driver (project stack, run from the worktree root).
Usage: python <this> ID[,ID...]    one mutant at a time: apply, run its nodes, restore, verify by sha256.
Verdict is per resolved node id (pytest -v), never the process exit code."""
import hashlib, re, subprocess, sys

HS, EN, RL = "tests/test_help_scope.py", "tests/test_en7.py", "tests/test_repair_layout.py"
AT = HS + "::test_at_008_the_own_keys_loop_is_deterministic_under_a_late_scroll"
N16 = HS + "::test_hlr_n16_4_legend_declares_its_own_keys"
FIX = HS + "::test_the_delay_fixture_delays_a_queued_scroll_only_inside_the_window"
HA = HS + "::test_llr_009_1_the_harvest_scroll_lands_before_it_is_read_under_a_late_scroll"
BA = HS + "::test_llr_009_1_the_bindings_scroll_lands_before_it_is_read_under_a_late_scroll"
EA = EN + "::test_the_painted_legend_ends_with_the_rule_under_a_late_scroll"
EB = EN + "::test_the_painted_legend_ends_with_the_rule"

EK_IMM = "pane.scroll_to(y=target, animate=False, immediate=True)\n        await pilot.pause()\n        assert pane.scroll_offset.y == target, \"the positioning scroll did not land\""
EK_ASSERT = "        assert pane.scroll_offset.y == target, \"the positioning scroll did not land\"\n"
H_IMM = "pane.scroll_to(y=target, animate=False, immediate=True)\n        await pilot.pause()\n        await pilot.pause()\n        assert pane.scroll_offset.y == min(target, pane.max_scroll_y), \"the harvest scroll did not land\""
B_IMM = "pane.scroll_to(y=target, animate=False, immediate=True)\n        await pilot.pause()\n        await pilot.pause()\n        assert pane.scroll_offset.y == min(target, pane.max_scroll_y), \"the bindings scroll did not land\""
E_IMM = "pane.scroll_to(y=target, animate=False, immediate=True)\n        await _settle(pilot)\n        assert pane.scroll_offset.y == target, \"the legend did not scroll to its end\""

def drop_imm(block): return block.replace(", immediate=True", "")
def drop_assert(block): return "\n".join(l for l in block.split("\n") if "did not" not in l or "scroll_to" in l)

M = {}
def add(i, f, old, new, nodes, note): M[i] = (f, old, new, nodes, note)
# site 1 :365 -> _effective_keys
add("S1-imm", HS, EK_IMM, drop_imm(EK_IMM), [AT, N16, FIX], "_effective_keys: drop immediate=True (settle assert kept)")
add("S1-both", HS, EK_IMM, drop_assert(drop_imm(EK_IMM)), [AT, N16, FIX], "_effective_keys: drop immediate=True AND the settle assert (the original FLAKE-2 step)")
add("S1-assert", HS, EK_ASSERT, "", [AT, N16, FIX], "_effective_keys: drop the settle assert only")
add("S1-halfwin", HS, "        with late_scroll():\n            pane.scroll_to(y=target, animate=False, immediate=True)", "        if True:\n            pane.scroll_to(y=target, animate=False, immediate=True)", [AT, N16, FIX], "_effective_keys: close the late window (equivalent while immediate holds)")
# fixture
add("F-off", HS, 'if _LATE["on"] and getattr', 'if False and getattr', [AT, FIX], "fixture: never delays")
add("F-zero", HS, "self.set_timer(0.15, lambda", "self.set_timer(0.0, lambda", [AT, FIX], "fixture: delay 0.15 -> 0.0")
add("F-always", HS, 'if _LATE["on"] and getattr', 'if getattr', [AT, N16, FIX], "fixture: delays regardless of the window")
add("F-both", HS, 'if _LATE["on"] and getattr', 'if False and getattr', [AT, FIX], "unused")
# site 2 :93 harvest
add("S2-imm", HS, H_IMM, drop_imm(H_IMM), [HA], "_harvest: drop immediate=True")
add("S2-both", HS, H_IMM, drop_assert(drop_imm(H_IMM)), [HA], "_harvest: drop immediate=True AND settle assert")
add("S2-assert", HS, "        assert pane.scroll_offset.y == min(target, pane.max_scroll_y), \"the harvest scroll did not land\"\n", "", [HA], "_harvest: drop settle assert only")
add("S2-min", HS, "== min(target, pane.max_scroll_y), \"the harvest", "== target, \"the harvest", [HA], "_harvest: settle assert without the min() clamp")
# site 3 :118 painted bindings
add("S3-imm", RL, B_IMM, drop_imm(B_IMM), [BA], "_painted_bindings: drop immediate=True")
add("S3-both", RL, B_IMM, drop_assert(drop_imm(B_IMM)), [BA], "_painted_bindings: drop immediate=True AND settle assert")
add("S3-assert", RL, "        assert pane.scroll_offset.y == min(target, pane.max_scroll_y), \"the bindings scroll did not land\"\n", "", [BA], "_painted_bindings: drop settle assert only")
add("S3-min", RL, "== min(target, pane.max_scroll_y), \"the bindings", "== target, \"the bindings", [BA], "_painted_bindings: settle assert without the min() clamp")
# site 4 :246 en7
add("S4-imm", EN, E_IMM, drop_imm(E_IMM), [EA, EB], "en7: drop immediate=True")
add("S4-both", EN, E_IMM, drop_assert(drop_imm(E_IMM)), [EA, EB], "en7: drop immediate=True AND settle assert")
add("S4-assert", EN, "        assert pane.scroll_offset.y == target, \"the legend did not scroll to its end\"\n", "", [EA, EB], "en7: drop settle assert only")
add("S4-guard", EN, "        assert target > 0, \"the legend fits; the scroll below would be a no-op\"\n", "", [EA, EB], "en7: drop the target>0 guard")
add("S4-guard-inv", EN, "assert target > 0,", "assert target > 10000,", [EA, EB], "en7: invert the target>0 guard (proves it can fire)")

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()

def run(i):
    f, old, new, nodes, note = M[i]
    before = sha(f); orig = open(f, "rb").read()
    o = old.replace("\n", "\r\n").encode(); n = new.replace("\n", "\r\n").encode()
    print(f"=== {i}: {note}\nfile {f}\nsha256 before {before}")
    if orig.count(o) != 1:
        print(f"BAD: anchor applies {orig.count(o)} times"); return
    try:
        open(f, "wb").write(orig.replace(o, n))
        print(f"sha256 mutated {sha(f)}  (changed: {sha(f) != before})")
        r = subprocess.run([sys.executable, "-B", "-W", "error::SyntaxWarning", "-m", "pytest", "-v", "-p", "no:cacheprovider", "--timeout=0", *nodes], capture_output=True, text=True)
        out = r.stdout
        for l in out.splitlines():
            if re.search(r"(PASSED|FAILED|ERROR)\s*(\[|$)", l) or "work but not painted" in l or "did not" in l and l.startswith("E"):
                print(l)
        print("summary:", out.strip().splitlines()[-1])
    finally:
        open(f, "wb").write(orig)
        after = sha(f)
        print(f"sha256 after restore {after}  restored: {after == before}\n")

for i in sys.argv[1].split(","): run(i)
