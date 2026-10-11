#!/usr/bin/env bash
# DDRFIX-A RED-proof driver — one arm per fix: backup (sha256), apply the
# named mutant, run the new node (expect RED), restore byte-identically
# (sha256 before == after), run the node again (expect GREEN).
# Run from the worktree root:  bash .dev-flow/2026-10-11-reqharness-batch/evidence/ddrfix-red.driver.sh
set -u
cd "$(dirname "$0")/../../.." || exit 1
ROOT="$(pwd)"
export PYTHONDONTWRITEBYTECODE=1
unset NO_COLOR 2>/dev/null || true
BACKUP="$ROOT/.dev-flow/2026-10-11-reqharness-batch/evidence/.ddrfix-backup"
rm -rf "$BACKUP"; mkdir -p "$BACKUP"
PATCHES="$BACKUP/patches"; mkdir -p "$PATCHES"
PY=python

sha() { sha256sum "$1" | cut -d' ' -f1; }

arm() {
  local name="$1" file="$2" node="$3" patch="$4"
  echo "=== ARM $name ==="
  echo "file:     $file"
  echo "node:     $node"
  cp "$ROOT/$file" "$BACKUP/$(basename "$file").orig"
  local before after
  before="$(sha "$ROOT/$file")"
  echo "sha256 before mutation: $before"
  "$PY" "$PATCHES/$patch" || { echo "MUTATION FAILED TO APPLY"; exit 1; }
  echo "--- RED run: python -B -m pytest -q -p no:cacheprovider $node"
  python -B -m pytest -q -p no:cacheprovider "$node" 2>&1 | grep -E "FAILED|failed|passed|Error" | tail -3
  local red="${PIPESTATUS[0]}"
  echo "RED run exit code: $red (nonzero == RED, as required)"
  cp "$BACKUP/$(basename "$file").orig" "$ROOT/$file"
  after="$(sha "$ROOT/$file")"
  echo "sha256 after restore:  $after"
  if [ "$before" = "$after" ]; then echo "restore: byte-identical"; else echo "restore: MISMATCH"; exit 1; fi
  echo "--- GREEN run: python -B -m pytest -q -p no:cacheprovider $node"
  python -B -m pytest -q -p no:cacheprovider "$node" 2>&1 | tail -1
  local green="${PIPESTATUS[0]}"
  echo "GREEN run exit code: $green (zero == GREEN, as required)"
  if [ "$red" -ne 1 ] || [ "$green" -ne 0 ]; then echo "ARM $name INVALID (red=$red green=$green)"; exit 1; fi
  echo ""
}

# --- mutation patches -----------------------------------------------------

cat > "$PATCHES/m_f1.py" <<'EOF'
import pathlib
p = pathlib.Path("mapper/reqharness/audit.py")
s = p.read_text(encoding="utf-8")
old = "if code < 0x20 or code == 0x7F or 0x80 <= code <= 0x9F:"
assert s.count(old) == 1, s.count(old)
p.write_text(s.replace(old, "if False:  # M-F1 escape disabled"), encoding="utf-8")
print("M-F1 applied: _visible escapes nothing")
EOF

cat > "$PATCHES/m_f2.py" <<'EOF'
import pathlib
p = pathlib.Path("mapper/reqharness/config.py")
s = p.read_text(encoding="utf-8")
old = "def _check_nesting(text: str, *, where: str) -> None:\n"
assert s.count(old) == 1, s.count(old)
p.write_text(s.replace(old, old + "    return  # M-F2 pre-scan disabled\n"), encoding="utf-8")
print("M-F2 applied: the nesting pre-scan is a no-op")
EOF

cat > "$PATCHES/m_f3.py" <<'EOF'
import pathlib
p = pathlib.Path("mapper/reqharness/chain.py")
s = p.read_text(encoding="utf-8")
old = "    resolved = _confine(repo, where)\n"
assert s.count(old) == 1, s.count(old)
p.write_text(s.replace(old, "    resolved = Path(repo) / where  # M-F3 confinement skipped\n"), encoding="utf-8")
print("M-F3 applied: _write_pending writes unconfined")
EOF

cat > "$PATCHES/m_f4a.py" <<'EOF'
import pathlib
p = pathlib.Path("mapper/reqharness/chain.py")
s = p.read_text(encoding="utf-8")
old = 'needs_newline = handle.read(1) != b"\\n"'
assert s.count(old) == 1, s.count(old)
p.write_text(s.replace(old, "needs_newline = False  # M-F4a repair disabled"), encoding="utf-8")
print("M-F4a applied: the missing trailing newline is never repaired")
EOF

cat > "$PATCHES/m_f4b.py" <<'EOF'
import pathlib
p = pathlib.Path("mapper/reqharness/chain.py")
s = p.read_text(encoding="utf-8")
old = "os.O_CREAT | os.O_EXCL | os.O_WRONLY"
assert s.count(old) == 1, s.count(old)
p.write_text(s.replace(old, "os.O_CREAT | os.O_WRONLY"), encoding="utf-8")
print("M-F4b applied: the append lock is not exclusive")
EOF

cat > "$PATCHES/m_f5.py" <<'EOF'
import pathlib
p = pathlib.Path("mapper/reqharness/chain.py")
s = p.read_text(encoding="utf-8")
old = (
    "        if event.request_hash is not None and event.approved_by == event.requested_by:\n"
    "            return False\n"
)
assert s.count(old) == 1, s.count(old)
p.write_text(s.replace(old, ""), encoding="utf-8")
print("M-F5 applied: the requester-approver walk rule is gone")
EOF

cat > "$PATCHES/m_c1.py" <<'EOF'
import pathlib
p = pathlib.Path("mapper/reqharness/audit.py")
s = p.read_text(encoding="utf-8")
old = (
    "    if not (root / REQHARNESS_DIR).is_dir():\n"
    "        return _no_registry_report(root)\n"
)
assert s.count(old) == 1, s.count(old)
p.write_text(s.replace(old, "    pass  # M-C1 no-registry state gone\n"), encoding="utf-8")
print("M-C1 applied: no-registry repos fall into the chain-broken path")
EOF

cat > "$PATCHES/m_c3.py" <<'EOF'
import pathlib
p = pathlib.Path("mapper/reqharness/chain.py")
s = p.read_text(encoding="utf-8")
s += (
    "\n\ndef _planted_scope_probe():\n"
    "    from mapper.reqharness.pending import list_pending  # M-C3 planted defect\n"
    "    return list_pending\n"
)
p.write_text(s, encoding="utf-8")
print("M-C3 applied: the chain<->pending back-edge is restored")
EOF

cat > "$PATCHES/m_c5.py" <<'EOF'
import pathlib
p = pathlib.Path("mapper/reqharness/audit.py")
s = p.read_text(encoding="utf-8")
old_import = "from mapper.osopen import is_link\n"
old_call = "        if is_link(info):\n"
assert s.count(old_import) == 1, s.count(old_import)
assert s.count(old_call) == 1, s.count(old_call)
s = s.replace(old_import, "")
s = s.replace(old_call, "        if _baseline._is_link(info):\n")
p.write_text(s, encoding="utf-8")
print("M-C5 applied: audit calls baseline._is_link again (osopen import gone)")
EOF

cat > "$PATCHES/m_fr3.py" <<'EOF'
import pathlib
p = pathlib.Path("mapper/reqharness/chain.py")
s = p.read_text(encoding="utf-8")
old = "        candidates = by_prev.get(head, [])\n"
assert s.count(old) == 1, s.count(old)
p.write_text(
    s.replace(
        old,
        "        candidates = [d for d in docs if id(d) not in consumed][:1]  # M-FR3 walks by file position\n",
    ),
    encoding="utf-8",
)
print("M-FR3 applied: the walk ignores prev_hash and takes file position")
EOF

cat > "$PATCHES/m_fr4.py" <<'EOF'
import pathlib
p = pathlib.Path("mapper/reqharness/chain.py")
s = p.read_text(encoding="utf-8")
old = (
    "    if not _passes_approval(child, report.events):\n"
    '        raise ValidationError(\n'
    '            "append_resolve: the chosen child fails the approval rule at its "\n'
    '            "own bound head"\n'
    "        )\n"
)
assert s.count(old) == 1, s.count(old)
p.write_text(s.replace(old, ""), encoding="utf-8")
print("M-FR4 applied: append_resolve may legitimate an unapprovable child")
EOF

cat > "$PATCHES/m_lm1.py" <<'EOF'
import pathlib
p = pathlib.Path("mapper/reqharness/config.py")
s = p.read_text(encoding="utf-8")
old = (
    "    if len(raw) > limit:\n"
    "        raise ValidationError(\n"
    '            f"{where}: file too large ({len(raw)} bytes > {limit} byte limit)"\n'
    "        )\n"
)
assert s.count(old) == 1, s.count(old)
p.write_text(s.replace(old, ""), encoding="utf-8")
print("M-LM1 applied: the size limit is skipped")
EOF

# --- arms ------------------------------------------------------------------

arm "M-F1 (SEC F1: render escapes registry-derived text)" \
    mapper/reqharness/audit.py \
    tests/test_reqharness_release.py::test_audit_render_escapes_registry_derived_text \
    m_f1.py

arm "M-F2 (SEC F2: nesting pre-scan)" \
    mapper/reqharness/config.py \
    tests/test_reqharness_config.py::test_nesting_prescan_refuses_superlinear_depth \
    m_f2.py

arm "M-F3 (SEC F3: pending confine-then-create)" \
    mapper/reqharness/chain.py \
    tests/test_reqharness_chain.py::test_pending_write_refuses_link_and_writes_nothing_outside \
    m_f3.py

arm "M-F4a (SEC F4 arm 1: trailing-newline repair)" \
    mapper/reqharness/chain.py \
    tests/test_reqharness_chain.py::test_roles_append_lock_repairs_newline_and_refuses_stale_lock \
    m_f4a.py

arm "M-F4b (SEC F4 arm 2: exclusive append lock)" \
    mapper/reqharness/chain.py \
    tests/test_reqharness_chain.py::test_roles_append_lock_repairs_newline_and_refuses_stale_lock \
    m_f4b.py

arm "M-F5 (SEC F5: requester-approver walk rule)" \
    mapper/reqharness/chain.py \
    tests/test_reqharness_chain.py::test_request_resolving_event_needs_alien_approver \
    m_f5.py

arm "M-C1 (QA C1: no-registry named state)" \
    mapper/reqharness/audit.py \
    tests/test_reqharness_release.py::test_audit_cli_names_no_registry_state \
    m_c1.py

arm "M-C3 (ARCH C3: chain<->pending cycle census)" \
    mapper/reqharness/chain.py \
    tests/test_reqharness_modgraph.py::test_no_reqharness_module_imports_a_module_that_imports_it_back \
    m_c3.py

arm "M-C5 (ARCH C5: audit uses the public osopen link helper)" \
    mapper/reqharness/audit.py \
    tests/test_arch_osopen_callers.py::test_outside_app_only_the_allowed_names_are_imported_from_osopen \
    m_c5.py

arm "M-FR3 (QA C2: verify walks by file position)" \
    mapper/reqharness/chain.py \
    tests/test_reqharness_chain.py::test_verify_walks_by_prev_hash_in_order_fork_resolve \
    m_fr3.py

arm "M-FR4 (QA C2: resolve legitimates an unapprovable child)" \
    mapper/reqharness/chain.py \
    tests/test_reqharness_chain.py::test_resolve_chosen_child_must_pass_approval_rule \
    m_fr4.py

arm "M-LM1 (QA C2: size limit skipped)" \
    mapper/reqharness/config.py \
    tests/test_reqharness_chain.py::test_input_limits_reported_by_name \
    m_lm1.py

echo "=== final state: full slice GREEN ==="
python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_*.py tests/test_no_operator_paths.py tests/test_arch_osopen_callers.py tests/test_mod_deps.py 2>&1 | tail -1
ruff check mapper/reqharness
echo "cleanup: backups removed"
rm -rf "$BACKUP"
echo "ALL ARMS RESOLVED"
