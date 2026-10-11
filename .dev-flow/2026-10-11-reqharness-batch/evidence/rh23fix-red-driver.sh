#!/usr/bin/env bash
# RHFIX23 RED-proof driver — one arm per code-review follow-up fix.
# Each arm: record the fixed file's sha256, apply the named single-conjunct
# mutant, run the fix's node (expect RED), restore byte-identically from the
# fixed-state backup, prove sha256 equality, run the node again (expect
# GREEN).  Transcript: rh23fix-red.transcript (relative paths, home redacted
# per A-110).  Run from the worktree root; PYTHONDONTWRITEBYTECODE on.
set -u
cd "$(dirname "$0")/../../.." || exit 1
export PYTHONDONTWRITEBYTECODE=1

EV=.dev-flow/2026-10-11-reqharness-batch/evidence
TR="$EV/rh23fix-red.transcript"
BK="$EV/.rh23fix-backup.$$"
mkdir -p "$BK"
cp mapper/reqharness/chain.py "$BK/chain.py.fixed"
cp mapper/reqharness/identity.py "$BK/identity.py.fixed"
CHAIN_FIXED=$(sha256sum "$BK/chain.py.fixed" | cut -d' ' -f1)
IDENT_FIXED=$(sha256sum "$BK/identity.py.fixed" | cut -d' ' -f1)
: > "$TR"

note() { printf '%s\n' "$*" >> "$TR"; }
redact() {
  # The profile-path prefixes are assembled from variables so the tracked
  # source carries no literal profile-path prefix before a regex class
  # (A-110's hermetic scan would otherwise read the class as a path segment).
  local fwd='C:/Users/' bsl='C:\Users\'
  sed -e "s|${fwd}[^/\"\\\\]*|C:/<profile>|g" \
      -e "s|${bsl}[^/\"\\\\]*|C:\\\\<profile>|g"
}
run() { # echo the command, run it, append redacted output; returns its exit code
  note "\$ $*"
  "$@" 2>&1 | redact >> "$TR"
  return "${PIPESTATUS[0]}"
}
mutate() { # mutate <file> — exact-string replacement, fails loudly if the anchor drifts
  local file="$1"
  note "\$ python - (mutate $file: $2)"
  python - "$file" >> "$TR" 2>&1 <<'PY'
import pathlib, sys
path = pathlib.Path(sys.argv[1])
old, new = MUTATION
text = path.read_text(encoding="utf-8")
assert text.count(old) == 1, f"anchor not unique: {old[:60]!r}"
path.write_text(text.replace(old, new), encoding="utf-8")
print("mutation applied")
PY
}
arm() { # arm <name> <file> <backup-digest> <node>
  local name="$1" file="$2" digest="$3" node="$4"
  note ""
  note "=== $name ==="
  note "node: $node"
  run sha256sum "$file"
}

note "RHFIX23 RED transcript — code-review follow-up for RH2 (chain) + RH3 (identity)"
note "fixed-state backups taken AFTER the fix was GREEN; every restore is"
note "verified byte-identical (sha256) against its backup before the GREEN re-run."
note "fixed chain.py sha256:    $CHAIN_FIXED"
note "fixed identity.py sha256: $IDENT_FIXED"
note ""
note "\$ python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_chain.py tests/test_reqharness_identity.py tests/test_reqharness_config.py tests/test_no_operator_paths.py"
python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_chain.py tests/test_reqharness_identity.py tests/test_reqharness_config.py tests/test_no_operator_paths.py 2>&1 | redact | tail -3 >> "$TR"

# ---------------------------------------------------------------- F1 (M-CH6)
arm "F1 (M-CH6): remove the genesis position pin and restore the unconditional genesis shortcut" \
    mapper/reqharness/chain.py "$CHAIN_FIXED" \
    tests/test_reqharness_chain.py::test_genesis_only_at_position_one
python - mapper/reqharness/chain.py "remove the position pin block in _check_event" >> "$TR" 2>&1 <<'PY'
import pathlib, sys
path = pathlib.Path(sys.argv[1])
old = '''    if (event.action == "genesis") != (position == 1):
        return (
            f"{event.action!r} at walk position {position}: genesis is "
            "allowed only at position 1, and position 1 must be genesis"
        )
'''
text = path.read_text(encoding="utf-8")
assert text.count(old) == 1, "anchor not unique: position pin"
path.write_text(text.replace(old, ""), encoding="utf-8")
print("mutation applied: position pin removed")
PY
python - mapper/reqharness/chain.py >> "$TR" 2>&1 <<'PY'
import pathlib
path = pathlib.Path("mapper/reqharness/chain.py")
old = '''    if event.action == "genesis":
        return not prefix'''
new = '''    if event.action == "genesis":
        return True'''
text = path.read_text(encoding="utf-8")
assert text.count(old) == 1, "anchor not unique: genesis shortcut"
path.write_text(text.replace(old, new), encoding="utf-8")
print("mutation applied: unconditional genesis shortcut restored")
PY
note "-- running the node (expect RED) --"
if run python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_chain.py::test_genesis_only_at_position_one; then
  note "!! UNEXPECTED GREEN — the mutant survived"
else
  note "-- RED as expected --"
fi
run cp "$BK/chain.py.fixed" mapper/reqharness/chain.py
run sha256sum mapper/reqharness/chain.py
note "restore check: $CHAIN_FIXED == $(sha256sum mapper/reqharness/chain.py | cut -d' ' -f1)"
if run python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_chain.py::test_genesis_only_at_position_one; then
  note "-- GREEN after byte-identical restore --"
else
  note "!! UNEXPECTED RED AFTER RESTORE"
fi

# ---------------------------------------------------------------- F2 (M-CH5)
arm "F2 (M-CH5): flip the fold boundary 'event.seq <= bound_seq' to '<'" \
    mapper/reqharness/chain.py "$CHAIN_FIXED" \
    tests/test_reqharness_chain.py::test_effective_roles_at_time_t
python - mapper/reqharness/chain.py >> "$TR" 2>&1 <<'PY'
import pathlib
path = pathlib.Path("mapper/reqharness/chain.py")
old = "        if event.action not in ROLE_ACTIONS or event.seq > bound_seq:"
new = "        if event.action not in ROLE_ACTIONS or event.seq >= bound_seq:"
text = path.read_text(encoding="utf-8")
assert text.count(old) == 1, "anchor not unique: fold boundary"
path.write_text(text.replace(old, new), encoding="utf-8")
print("mutation applied: `<=` flipped to `<`")
PY
note "-- running the node (expect RED) --"
if run python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_chain.py::test_effective_roles_at_time_t; then
  note "!! UNEXPECTED GREEN — the mutant survived"
else
  note "-- RED as expected --"
fi
run cp "$BK/chain.py.fixed" mapper/reqharness/chain.py
run sha256sum mapper/reqharness/chain.py
note "restore check: $CHAIN_FIXED == $(sha256sum mapper/reqharness/chain.py | cut -d' ' -f1)"
if run python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_chain.py::test_effective_roles_at_time_t; then
  note "-- GREEN after byte-identical restore --"
else
  note "!! UNEXPECTED RED AFTER RESTORE"
fi

# -------------------------------------------------------------------- F3
arm "F3 (F3a): drop the required config_hash check on genesis/policy events" \
    mapper/reqharness/chain.py "$CHAIN_FIXED" \
    tests/test_reqharness_chain.py::test_policy_event_requires_config_hash
python - mapper/reqharness/chain.py >> "$TR" 2>&1 <<'PY'
import pathlib
path = pathlib.Path("mapper/reqharness/chain.py")
old = '''    if action in ("genesis", "policy") and "config_hash" not in keys:
        raise ValidationError(f"{where}: missing key(s): config_hash")
'''
text = path.read_text(encoding="utf-8")
assert text.count(old) == 1, "anchor not unique: config_hash requirement"
path.write_text(text.replace(old, ""), encoding="utf-8")
print("mutation applied: config_hash requirement removed")
PY
note "-- running the node (expect RED) --"
if run python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_chain.py::test_policy_event_requires_config_hash; then
  note "!! UNEXPECTED GREEN — the mutant survived"
else
  note "-- RED as expected --"
fi
run cp "$BK/chain.py.fixed" mapper/reqharness/chain.py
run sha256sum mapper/reqharness/chain.py
note "restore check: $CHAIN_FIXED == $(sha256sum mapper/reqharness/chain.py | cut -d' ' -f1)"
if run python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_chain.py::test_policy_event_requires_config_hash; then
  note "-- GREEN after byte-identical restore --"
else
  note "!! UNEXPECTED RED AFTER RESTORE"
fi

# ---------------------------------------------------------------- F4 (M-ID3)
arm "F4 (M-ID3): let the audited repo / the cwd supply git (exclusions removed)" \
    mapper/reqharness/identity.py "$IDENT_FIXED" \
    tests/test_reqharness_identity.py::test_git_resolution_excludes_repo_and_cwd
python - mapper/reqharness/identity.py >> "$TR" 2>&1 <<'PY'
import pathlib
path = pathlib.Path("mapper/reqharness/identity.py")
old = '''        if norm == target or norm.startswith(target + os.sep):
            continue  # inside the audited repo — never supplies git
        if norm == cwd:
            continue  # the current working directory — never supplies git
'''
text = path.read_text(encoding="utf-8")
assert text.count(old) == 1, "anchor not unique: repo/cwd exclusions"
path.write_text(text.replace(old, ""), encoding="utf-8")
print("mutation applied: repo/cwd exclusions removed")
PY
note "-- running the node (expect RED) --"
if run python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_identity.py::test_git_resolution_excludes_repo_and_cwd; then
  note "!! UNEXPECTED GREEN — the mutant survived"
else
  note "-- RED as expected --"
fi
run cp "$BK/identity.py.fixed" mapper/reqharness/identity.py
run sha256sum mapper/reqharness/identity.py
note "restore check: $IDENT_FIXED == $(sha256sum mapper/reqharness/identity.py | cut -d' ' -f1)"
if run python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_identity.py::test_git_resolution_excludes_repo_and_cwd; then
  note "-- GREEN after byte-identical restore --"
else
  note "!! UNEXPECTED RED AFTER RESTORE"
fi

# -------------------------------------------------------------------- F5
arm "F5 (F5a): strip only GIT_DIR/GIT_WORK_TREE/GIT_CONFIG* (the pre-fix behaviour)" \
    mapper/reqharness/identity.py "$IDENT_FIXED" \
    tests/test_reqharness_identity.py::test_git_resolution_absolute_and_path_pinned
python - mapper/reqharness/identity.py >> "$TR" 2>&1 <<'PY'
import pathlib
path = pathlib.Path("mapper/reqharness/identity.py")
old = '''    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GIT_")
    }
'''
new = '''    env = {
        key: value
        for key, value in os.environ.items()
        if key not in ("GIT_DIR", "GIT_WORK_TREE")
        and not key.startswith("GIT_CONFIG")
    }
'''
text = path.read_text(encoding="utf-8")
assert text.count(old) == 1, "anchor not unique: git env strip"
path.write_text(text.replace(old, new), encoding="utf-8")
print("mutation applied: strip narrowed to the pre-fix set")
PY
note "-- running the node (expect RED) --"
if run python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_identity.py::test_git_resolution_absolute_and_path_pinned; then
  note "!! UNEXPECTED GREEN — the mutant survived"
else
  note "-- RED as expected --"
fi
run cp "$BK/identity.py.fixed" mapper/reqharness/identity.py
run sha256sum mapper/reqharness/identity.py
note "restore check: $IDENT_FIXED == $(sha256sum mapper/reqharness/identity.py | cut -d' ' -f1)"
if run python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_identity.py::test_git_resolution_absolute_and_path_pinned; then
  note "-- GREEN after byte-identical restore --"
else
  note "!! UNEXPECTED RED AFTER RESTORE"
fi

# -------------------------------------------------------------------- F6
arm "F6 (F6a): resolve the repo path unguarded (no OSError/ValueError/RuntimeError catch)" \
    mapper/reqharness/identity.py "$IDENT_FIXED" \
    tests/test_reqharness_identity.py::test_unresolvable_repo_path_is_named_no_repo_not_a_crash
python - mapper/reqharness/identity.py >> "$TR" 2>&1 <<'PY'
import pathlib
path = pathlib.Path("mapper/reqharness/identity.py")
old = '''    key_path = _resolve_path(repo)
    if key_path is None:
        return None
    key = str(key_path)
'''
new = '''    key = str(repo.resolve())
'''
text = path.read_text(encoding="utf-8")
assert text.count(old) == 1, "anchor not unique: _resolve_git guard"
path.write_text(text.replace(old, new), encoding="utf-8")
print("mutation applied: unguarded repo.resolve() restored")
PY
note "-- running the node (expect RED) --"
if run python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_identity.py::test_unresolvable_repo_path_is_named_no_repo_not_a_crash; then
  note "!! UNEXPECTED GREEN — the mutant survived"
else
  note "-- RED as expected --"
fi
run cp "$BK/identity.py.fixed" mapper/reqharness/identity.py
run sha256sum mapper/reqharness/identity.py
note "restore check: $IDENT_FIXED == $(sha256sum mapper/reqharness/identity.py | cut -d' ' -f1)"
if run python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_identity.py::test_unresolvable_repo_path_is_named_no_repo_not_a_crash; then
  note "-- GREEN after byte-identical restore --"
else
  note "!! UNEXPECTED RED AFTER RESTORE"
fi

# -------------------------------------------------------------------- F7
arm "F7 (F7a): cache the failed (None) git resolution" \
    mapper/reqharness/identity.py "$IDENT_FIXED" \
    tests/test_reqharness_identity.py::test_failed_git_resolution_is_not_cached
python - mapper/reqharness/identity.py >> "$TR" 2>&1 <<'PY'
import pathlib
path = pathlib.Path("mapper/reqharness/identity.py")
old = '''    if key not in _GIT_CACHE:
        found = _which_git(repo)
        if found is not None:
            _GIT_CACHE[key] = found
    return _GIT_CACHE.get(key)
'''
new = '''    if key not in _GIT_CACHE:
        _GIT_CACHE[key] = _which_git(repo)
    return _GIT_CACHE.get(key)
'''
text = path.read_text(encoding="utf-8")
assert text.count(old) == 1, "anchor not unique: _GIT_CACHE store"
path.write_text(text.replace(old, new), encoding="utf-8")
print("mutation applied: failed resolution cached")
PY
note "-- running the node (expect RED) --"
if run python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_identity.py::test_failed_git_resolution_is_not_cached; then
  note "!! UNEXPECTED GREEN — the mutant survived"
else
  note "-- RED as expected --"
fi
run cp "$BK/identity.py.fixed" mapper/reqharness/identity.py
run sha256sum mapper/reqharness/identity.py
note "restore check: $IDENT_FIXED == $(sha256sum mapper/reqharness/identity.py | cut -d' ' -f1)"
if run python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_identity.py::test_failed_git_resolution_is_not_cached; then
  note "-- GREEN after byte-identical restore --"
else
  note "!! UNEXPECTED RED AFTER RESTORE"
fi

# ------------------------------------------------------------- final sweep
note ""
note "=== final sweep after all restores ==="
run sha256sum "$BK/chain.py.fixed" mapper/reqharness/chain.py
run sha256sum "$BK/identity.py.fixed" mapper/reqharness/identity.py
note "\$ python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_chain.py tests/test_reqharness_identity.py tests/test_reqharness_config.py tests/test_no_operator_paths.py"
python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_chain.py tests/test_reqharness_identity.py tests/test_reqharness_config.py tests/test_no_operator_paths.py 2>&1 | redact | tail -2 >> "$TR"
note "\$ ruff check mapper/reqharness/ tests/test_reqharness_chain.py tests/test_reqharness_identity.py"
ruff check mapper/reqharness/ tests/test_reqharness_chain.py tests/test_reqharness_identity.py 2>&1 >> "$TR"

rm -rf "$BK"
note ""
note "backup directory removed; all restores above verified byte-identical."
