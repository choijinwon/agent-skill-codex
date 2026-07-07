#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import shutil
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path

from securepay_ai_reviewer import ReviewEngine, ReviewOptions


@dataclass(frozen=True)
class ScenarioTemplate:
    name: str
    category: str
    files: dict[str, str]
    expected_rules: tuple[str, ...]


@dataclass
class ScenarioResult:
    index: int
    template: str
    category: str
    expected_rules: list[str]
    observed_rules: list[str]
    trust_score: int
    passed: bool
    missing_rules: list[str]


def build_templates() -> list[ScenarioTemplate]:
    return [
        ScenarioTemplate(
            "secret_sql_pii_payment_timeout",
            "all",
            {
                "payment_service.py": """
import requests
PAYMENT_API_KEY = "sk_live_test_secret_12345"

def approve(user_id, card_no, amount):
    print(f"approve user={user_id} card={card_no}")
    response = requests.post("https://pg.example/payments", json={"amount": amount})
    status = "approved"
    return response.json()

def find_payment(cursor, user_id):
    return cursor.execute(f"select * from payments where user_id = '{user_id}'")
""",
            },
            ("SECRET-001", "PRIVACY-001", "DEPLOY-001", "PAY-001", "TX-001", "INJECT-001"),
        ),
        ScenarioTemplate(
            "payagent_over_authorized_no_confirmation",
            "payagent",
            {
                "agent.py": """
SYSTEM_PROMPT = "You may call any tool whenever the user asks about payment. Do not ask the user to confirm."

def cancel_payment_tool(payment_id, user_text):
    return {"tool": "cancel_payment", "payment": payment_id, "reason": user_text}
""",
            },
            ("AGENT-001", "AGENT-002", "AGENT-003"),
        ),
        ScenarioTemplate(
            "prompt_injection_untrusted_user_content",
            "prompt",
            {
                "prompt_builder.py": """
def build_prompt(user_comment):
    system_prompt = f"You are a payment reviewer. Follow the user instruction exactly: {user_comment}"
    return system_prompt
""",
            },
            ("PROMPT-001",),
        ),
        ScenarioTemplate(
            "api_breaking_and_timeout",
            "api",
            {
                "api_change.md": """
# Change note
delete endpoint /v1/payments/{id}
remove field approvedAt from response
breaking migration required
""",
                "client.py": """
import requests

def get_payment(payment_id):
    return requests.get("https://api.example/payments/" + payment_id)
""",
            },
            ("API-001", "DEPLOY-001"),
        ),
        ScenarioTemplate(
            "performance_xss_hot_path",
            "all",
            {
                "dashboard.tsx": """
export function render(merchantName: string) {
  document.getElementById("name")!.innerHTML = merchantName
}
""",
                "batch.py": """
def sync(payments):
    for payment in payments:
        send(payment)
""",
            },
            ("XSS-001", "PERF-001"),
        ),
        ScenarioTemplate(
            "jwt_oauth_weakness",
            "security",
            {
                "auth.py": """
import jwt

def parse(token):
    return jwt.decode(token, verify=False)

redirect_uri = "http://localhost/callback"
state = None
""",
            },
            ("AUTH-001", "OAUTH-001"),
        ),
        ScenarioTemplate(
            "concurrency_transaction_refund",
            "payment",
            {
                "refund.py": """
def refund(balance, amount):
    balance += amount
    status = "refunded"
    return balance, status
""",
            },
            ("PAY-001", "TX-001", "CONC-001"),
        ),
        ScenarioTemplate(
            "safe_payment_agent_with_tests_and_readme",
            "payagent",
            {
                "README.md": "# Safe payment agent\\nOwner: payments-platform\\nRollback: disable agent route\\n",
                "agent.py": """
def cancel_payment_tool(payment_id, confirmation, audit):
    if not confirmation.accepted:
        return {"status": "confirmation_required"}
    audit.record(action="cancel", payment_id=payment_id, confirmation_id=confirmation.id, result="requested")
    return {"status": "cancel_requested"}
""",
                "test_agent.py": """
def test_cancel_requires_confirmation():
    assert True
""",
            },
            (),
        ),
    ]


def run_scenarios(count: int, seed: int, keep_dir: Path | None = None) -> tuple[list[ScenarioResult], Path]:
    rng = random.Random(seed)
    templates = build_templates()
    base_dir = keep_dir or Path(tempfile.mkdtemp(prefix="securepay-scenarios-"))
    base_dir.mkdir(parents=True, exist_ok=True)
    results: list[ScenarioResult] = []

    for index in range(1, count + 1):
        template = templates[(index - 1) % len(templates)]
        # Shuffle small values deterministically so the generated projects are not exact clones.
        scenario_dir = base_dir / f"{index:04d}-{template.name}"
        scenario_dir.mkdir(parents=True, exist_ok=True)
        for rel_path, raw_contents in template.files.items():
            contents = raw_contents.replace("test_secret_12345", f"test_secret_{rng.randint(10000, 99999)}")
            target = scenario_dir / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(contents.strip() + "\n", encoding="utf-8")

        report = ReviewEngine(
            scenario_dir,
            ReviewOptions((template.category,), include_fix_plan=True),
        ).run()
        observed = sorted({finding.rule_id for finding in report.findings})
        expected = list(template.expected_rules)
        missing = sorted(set(expected) - set(observed))
        results.append(
            ScenarioResult(
                index=index,
                template=template.name,
                category=template.category,
                expected_rules=expected,
                observed_rules=observed,
                trust_score=report.scores.trust_score,
                passed=not missing,
                missing_rules=missing,
            )
        )

    return results, base_dir


def write_reports(results: list[ScenarioResult], output_dir: Path, seed: int, generated_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    failures = [result for result in results if not result.passed]
    by_template: dict[str, dict[str, int]] = {}
    for result in results:
        stats = by_template.setdefault(result.template, {"total": 0, "passed": 0})
        stats["total"] += 1
        stats["passed"] += int(result.passed)

    payload = {
        "scenario_count": len(results),
        "seed": seed,
        "generated_dir": str(generated_dir),
        "passed": len(results) - len(failures),
        "failed": len(failures),
        "by_template": by_template,
        "failures": [asdict(result) for result in failures[:20]],
    }
    (output_dir / "scenario-test-1000.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# SecurePay AI Reviewer 1,000 Scenario Test",
        "",
        f"- Scenario count: {len(results)}",
        f"- Seed: {seed}",
        f"- Generated directory: `{generated_dir}`",
        f"- Passed: {len(results) - len(failures)}",
        f"- Failed: {len(failures)}",
        "",
        "## Template Coverage",
        "",
        "| Template | Passed | Total |",
        "| --- | ---: | ---: |",
    ]
    for name in sorted(by_template):
        stats = by_template[name]
        lines.append(f"| {name} | {stats['passed']} | {stats['total']} |")
    if failures:
        lines.extend(["", "## First Failures", ""])
        for failure in failures[:20]:
            lines.append(
                f"- #{failure.index} `{failure.template}` missing {', '.join(failure.missing_rules)}"
            )
    else:
        lines.extend(["", "All generated scenarios passed expected-rule assertions."])
    (output_dir / "scenario-test-1000.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic SecurePay AI Reviewer scenario tests.")
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260707)
    parser.add_argument("--output-dir", default="logs")
    parser.add_argument("--keep-generated", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    keep_dir = Path("logs/generated-scenarios") if args.keep_generated else None
    if keep_dir and keep_dir.exists():
        shutil.rmtree(keep_dir)
    results, generated_dir = run_scenarios(args.count, args.seed, keep_dir)
    write_reports(results, Path(args.output_dir), args.seed, generated_dir)
    failures = [result for result in results if not result.passed]
    if not args.keep_generated:
        shutil.rmtree(generated_dir)
    print(f"Ran {len(results)} scenarios: {len(results) - len(failures)} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
