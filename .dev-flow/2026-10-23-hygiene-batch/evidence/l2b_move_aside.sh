#!/usr/bin/env bash
# L2b move-aside RED counterfactual (C11 habit 1) — per deliverable file:
# hash before, rename aside, run its holding arms (must go RED), restore,
# hash after (must equal before). Run from the worktree root under
# `env -u NO_COLOR -u TERM`. PYTHONDONTWRITEBYTECODE=1 (C-46).
set -u
export PYTHONDONTWRITEBYTECODE=1
PY="python -B -m pytest -q -p no:cacheprovider"

aside() { # <file> <arms...>
  local f="$1"; shift
  local h0
  h0=$(sha256sum "$f" | cut -d' ' -f1)
  echo "== $f aside =="
  echo "before: $h0"
  mv "$f" "$f.__aside__"
  env -u NO_COLOR -u TERM $PY "$@" 2>&1 | tail -6
  echo "arm exit: ${PIPESTATUS[0]}"
  mv "$f.__aside__" "$f"
  local h1
  h1=$(sha256sum "$f" | cut -d' ' -f1)
  echo "after:  $h1"
  if [ "$h0" = "$h1" ]; then echo "restore: PROVEN (hash equal)"; else echo "restore: FAILED"; exit 1; fi
  echo
}

aside mapper/import_csv.py tests/test_ingestion_limits.py tests/test_import_csv.py
aside mapper/screens/home.py tests/test_ingestion_limits.py::test_at_114_csv_refusal_toast_shows_the_reason tests/test_app.py
echo "all move-asides done"
