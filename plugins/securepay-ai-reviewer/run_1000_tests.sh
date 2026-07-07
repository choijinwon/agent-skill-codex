#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

echo "== SecurePay AI Reviewer 1,000 scenario validation =="
python3 scripts/run_scenario_tests.py --count 1000 --output-dir logs

