#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PLUGIN_DIR="$SCRIPT_DIR/plugins/securepay-ai-reviewer"

if [ ! -d "$PLUGIN_DIR" ]; then
  echo "SecurePay plugin directory not found: $PLUGIN_DIR" >&2
  exit 1
fi

cd "$PLUGIN_DIR"

echo "== SecurePay AI Reviewer 1,000 scenario validation =="
python3 scripts/run_scenario_tests.py --count 1000 --output-dir logs

