#!/usr/bin/env bash
# RH1 RED-proof battery — UNIT RHI1 (batch 2026-10-11-reqharness-batch).
# Each arm: record sha256 -> mutate the product -> named node RED ->
# restore byte-identically -> sha256 equal -> GREEN. Run from the worktree root.
set -u
cd "$(dirname "$0")/../../.." || exit 1
export PYTHONDONTWRITEBYTECODE=1
TESTFILE="tests/test_reqharness_config.py"
TR=".dev-flow/2026-10-11-reqharness-batch/evidence/rh1-red.transcript"
: > "$TR"

say() { echo "$@" | tee -a "$TR"; }

run_node() {  # <node suffix>
  python -m pytest -p no:cacheprovider "$TESTFILE::$1" 2>&1 | grep -E "PASSED|FAILED|ERROR|passed|failed|error" | tail -3
}

mutate() {  # <file> <python-mutation-source>
  python - "$@" <<'PYEOF'
import sys
path, src = sys.argv[1], sys.argv[2]
code = open(path, encoding="utf-8").read()
ns = {}
exec(src, ns)
old, new = ns["OLD"], ns["NEW"]
assert code.count(old) == 1, f"anchor count={code.count(old)}"
open(path, "w", encoding="utf-8", newline="").write(code.replace(old, new))
print("mutation applied")
PYEOF
}

arm() {  # <id> <file> <node> <mutation-src>
  local id="$1" file="$2" node="$3" src="$4"
  say ""
  say "=== $id : $file -> $node ==="
  local before
  before=$(sha256sum "$file" | cut -d" " -f1)
  say "sha256 before: $before"
  cp "$file" "$file.rh1keep"
  mutate "$file" "$src" | tee -a "$TR"
  say "--- RED run: pytest $TESTFILE::$node"
  run_node "$node" | tee -a "$TR"
  mv "$file.rh1keep" "$file"
  local after
  after=$(sha256sum "$file" | cut -d" " -f1)
  say "sha256 after:  $after"
  if [ "$before" = "$after" ]; then say "restore: BYTE-IDENTICAL"; else say "restore: MISMATCH"; fi
  say "--- GREEN run: pytest $TESTFILE::$node"
  run_node "$node" | tee -a "$TR"
}

CFG="mapper/reqharness/config.py"
CAN="mapper/reqharness/canonical.py"

say "UNIT RHI1 — RH1 RED proof — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
say "worktree: $(pwd)"
say "PYTHONDONTWRITEBYTECODE=1; pytest -p no:cacheprovider; single file only"

# M-CF1 — genesis prev_hash altered
arm "M-CF1" "$CFG" "test_genesis_creates_chain_with_declared_admin" '
OLD = "        \"prev_hash\": GENESIS_PREV,\n"
NEW = "        \"prev_hash\": \"TAMPERED\",\n"
'

# M-CF2 — reviewer-role cross-check removed
arm "M-CF2" "$CFG" "test_load_rejects_unknown_reviewer_role" '
OLD = "        if cls.reviewer_role not in role_ids:\n"
NEW = "        if False:  # M-CF2: cross-check removed\n"
'

# M-CJ1 — concatenation of values hashed instead of the canonical JSON object
arm "M-CJ1" "$CAN" "test_canonical_json_typed_schema" '
OLD = "    return hashlib.sha256(canonical_json(value).encode(\"utf-8\")).hexdigest()\n"
NEW = "    return hashlib.sha256(\"\".join(str(v) for v in value.values()).encode(\"utf-8\")).hexdigest()\n"
'

# M-EH1 — email stored in clear
arm "M-EH1" "$CFG" "test_email_sha256_roundtrip" '
OLD = "                {\"id\": person, \"name\": name, \"email_sha256\": email_sha256(email)}\n"
NEW = "                {\"id\": person, \"name\": name, \"email_sha256\": email}\n"
'

# M-YC1 — a load routed through yaml.load: the census instrument must report it.
say ""
say "=== M-YC1 : $CFG — census instrument (grep over mapper/reqharness/) ==="
before=$(sha256sum "$CFG" | cut -d" " -f1)
say "sha256 before: $before"
cp "$CFG" "$CFG.rh1keep"
mutate "$CFG" '
OLD = "        return list(yaml.load_all(text, Loader=ReqHarnessLoader))\n"
NEW = "        return list(yaml.load(text, Loader=yaml.SafeLoader))\n"
' | tee -a "$TR"
say "--- census run: grep -rnE 'yaml\\.load\\(|FullLoader' mapper/reqharness/"
grep -rnE "yaml\.load\(|FullLoader" mapper/reqharness/ | tee -a "$TR"
say "census verdict: $(grep -rcE "yaml\.load\(|FullLoader" mapper/reqharness/*.py | grep -v ':0' | wc -l) file(s) with a hit — census FAILURE reported"
mv "$CFG.rh1keep" "$CFG"
after=$(sha256sum "$CFG" | cut -d" " -f1)
say "sha256 after:  $after"
if [ "$before" = "$after" ]; then say "restore: BYTE-IDENTICAL"; else say "restore: MISMATCH"; fi
say "--- GREEN run: grep census"
grep -rnE "yaml\.load\(|FullLoader" mapper/reqharness/ | tee -a "$TR"
say "census verdict: 0 hits — clean"

say ""
say "=== final GREEN: full $TESTFILE ==="
python -m pytest -p no:cacheprovider "$TESTFILE" 2>&1 | tail -2 | tee -a "$TR"
say "=== guard tests after all restores ==="
python -m pytest -p no:cacheprovider tests/test_repair_map_truth.py tests/test_arch_osopen_callers.py tests/test_no_operator_paths.py -q 2>&1 | tail -2 | tee -a "$TR"
say "=== ruff on new files ==="
ruff check mapper/reqharness/ tests/test_reqharness_config.py 2>&1 | tee -a "$TR"
