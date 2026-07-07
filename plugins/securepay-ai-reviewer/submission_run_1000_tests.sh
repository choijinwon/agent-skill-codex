#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SRC_DIR="$SCRIPT_DIR/src"

if [ ! -d "$SRC_DIR" ]; then
  echo "submission src directory not found: $SRC_DIR" >&2
  echo "Run this script from the unzipped submission root." >&2
  exit 1
fi

cd "$SRC_DIR"

echo "== SecurePay AI Reviewer 1,000 scenario validation =="
python3 scripts/run_scenario_tests.py --count 1000 --output-dir ../logs

