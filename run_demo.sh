#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PLUGIN_DIR="$SCRIPT_DIR/plugins/securepay-ai-reviewer"

if [ ! -d "$PLUGIN_DIR" ]; then
  echo "SecurePay plugin directory not found: $PLUGIN_DIR" >&2
  exit 1
fi

cd "$PLUGIN_DIR"

echo "== SecurePay AI Reviewer demo =="
echo
echo "[1/2] Payment service review"
python3 scripts/securepay_review.py samples/payment-service --category payment
echo
echo "[2/2] Payment AI Agent review"
python3 scripts/securepay_review.py samples/payment-agent --category payagent

