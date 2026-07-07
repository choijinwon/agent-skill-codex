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

echo "== SecurePay AI Reviewer demo =="
echo
echo "[1/2] Payment service review"
python3 scripts/securepay_review.py samples/payment-service --category payment
echo
echo "[2/2] Payment AI Agent review"
python3 scripts/securepay_review.py samples/payment-agent --category payagent

