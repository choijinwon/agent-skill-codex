#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

echo "== SecurePay AI Reviewer demo =="
echo
echo "[1/2] Payment service review"
python3 scripts/securepay_review.py samples/payment-service --category payment
echo
echo "[2/2] Payment AI Agent review"
python3 scripts/securepay_review.py samples/payment-agent --category payagent

