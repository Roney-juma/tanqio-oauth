#!/usr/bin/env bash
set -euo pipefail

files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(yml|yaml)$' || true)
if [ -z "$files" ]; then
  exit 0
fi

bad=0
while IFS= read -r f; do
  if grep -nP '\t' "$f" >/dev/null 2>&1; then
    echo "YAML tab indentation violation in: $f" >&2
    grep -nP '\t' "$f" | sed 's/\t/[TAB]/g'
    bad=1
  fi
done <<< "$files"

if [ $bad -ne 0 ]; then
  echo "\nCommit rejected: Remove tabs (replace with spaces) in YAML files above." >&2
  exit 1
fi
exit 0
