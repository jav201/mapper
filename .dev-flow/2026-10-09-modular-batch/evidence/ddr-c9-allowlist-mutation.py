"""PDR C9 / LLR-MOD.5.2: execute the §5 allow-list timing mutation on a tmp copy (RED expected)."""
import shutil, subprocess, sys, tempfile
from pathlib import Path

REPO = Path(sys.argv[1])
T = "tests/test_arch_osopen_callers.py"
ORIG = 'ALLOWED_FILES = {"osopen.py", "screens/map/opening.py"}'
MUTANTS = {
    "not-extended-after (opening.py dropped)": 'ALLOWED_FILES = {"osopen.py"}',
    "extended-before (a file without the call listed)":
        'ALLOWED_FILES = {"osopen.py", "screens/map/opening.py", "screens/map/screen.py"}',
}
NODE = "::test_the_launcher_names_appear_only_in_app_and_osopen"


def run(root):
    r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", T + NODE],
                       cwd=root, capture_output=True, text=True)
    return r.returncode, r.stdout.strip().splitlines()[-1]


with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    for sub in ("mapper", "tests"):
        shutil.copytree(REPO / sub, root / sub, ignore=shutil.ignore_patterns("__pycache__"))
    for f in ("pyproject.toml", "conftest.py"):
        if (REPO / f).exists():
            shutil.copy2(REPO / f, root / f)
    src = (root / T).read_text(encoding="utf-8")
    assert src.count(ORIG) == 1
    rc, tail = run(root)
    print(f"GREEN baseline: exit={rc} | {tail}")
    ok = rc == 0
    for name, mut in MUTANTS.items():
        (root / T).write_text(src.replace(ORIG, mut), encoding="utf-8")
        rc, tail = run(root)
        print(f"RED {name}: exit={rc} | {tail}")
        ok &= rc != 0
    (root / T).write_text(src, encoding="utf-8")
    rc, tail = run(root)
    print(f"GREEN restored: exit={rc} | {tail}")
    ok &= rc == 0
print("VERDICT:", "both mutants RED, baseline and restore GREEN" if ok else "FAILED")
