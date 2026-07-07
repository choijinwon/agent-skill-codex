#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from securepay_ai_reviewer import ReviewEngine, ReviewOptions


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="securepay_review",
        description="Financial code review rule engine for SecurePay AI Reviewer.",
    )
    parser.add_argument("target", help="File or directory to review.")
    parser.add_argument(
        "--category",
        action="append",
        default=[],
        choices=["all", "security", "api", "performance", "payment", "prompt", "agent", "payagent"],
        help="Review profile. Can be repeated. Defaults to all.",
    )
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", help="Write report to this file.")
    parser.add_argument("--no-fix-plan", action="store_true", help="Hide auto-fix suggestions.")
    parser.add_argument("--fail-under", type=int, default=0, help="Exit 2 if Trust Score is below this threshold.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    target = Path(args.target)
    if not target.exists():
        print(f"Target does not exist: {target}", file=sys.stderr)
        return 1

    categories = tuple(args.category or ["all"])
    report = ReviewEngine(target, ReviewOptions(categories, not args.no_fix_plan)).run()
    rendered = report.to_json() if args.format == "json" else report.to_markdown()

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    if args.fail_under and report.scores.trust_score < args.fail_under:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
